"""把多个 Agent 编排成一次完整研究任务。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
from app.domain.events import ResearchEvent
from app.domain.state import ResearchState


class ResearchWorkflow:
    """Iteration 01 的最小研究编排器。

    每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
    ``run`` 适合一次性拿到结果，``stream`` 适合逐步消费进度事件。
    SSE 和数据库等外层能力后续再加入；审核修订循环在本轮实现。
    """

    def __init__(
        self,
        llm: LLMClient,
        search: SearchClient,
        results_per_question: int = 3,
        max_iterations: int = 1,
    ):
        if max_iterations < 0:
            raise ValueError("max_iterations 不能小于 0")
        self.max_iterations = max_iterations
        self.planner = PlannerAgent(llm)
        self.researcher = ResearcherAgent(search, results_per_question)
        self.fact_extractor = FactExtractorAgent(llm)
        self.writer = WriterAgent(llm)
        self.critic = CriticAgent(llm)

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        """执行一次完整研究并返回最终状态。"""
        state = self._new_state(query, session_id)
        async for _ in self._stream_state(state):
            # run 保留一次性调用方式，只忽略中间事件。
            pass
        return state

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """逐步产出研究进度事件，最后一个事件包含完整结果。

        这个方法仍然使用和 ``run`` 相同的 Agent 和状态对象，因此不会
        产生两套业务逻辑。当前返回普通字典，后续接 FastAPI SSE 时可以
        直接序列化；暂时不需要启动真实服务就能测试事件顺序。
        """
        state = self._new_state(query, session_id)
        async for event in self._stream_state(state):
            yield event

    def _new_state(
        self,
        query: str,
        session_id: str | None,
    ) -> ResearchState:
        """创建一次研究任务的初始状态。"""
        return ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
            max_iterations=self.max_iterations,
        )

    async def _stream_state(
        self,
        state: ResearchState,
    ) -> AsyncIterator[dict[str, Any]]:
        """执行工作流并发布事件；``run`` 和 ``stream`` 共用此实现。"""
        yield self._event(
            state,
            "research_started",
            query=state.query,
            max_iterations=state.max_iterations,
        )

        yield self._event(
            state,
            "phase_started",
            phase="planning",
            agent=self.planner.name,
        )
        await self.planner.run(state)
        yield self._event(
            state,
            "outline_ready",
            outline=state.outline,
            research_questions=state.research_questions,
        )

        async for event in self._run_research_phase(state, supplementary=False):
            yield event
        yield self._event(
            state,
            "phase_started",
            phase="writing",
            agent=self.writer.name,
        )
        await self.writer.run(state)
        yield self._event(
            state,
            "draft_ready",
            report=state.final_report,
            revision=False,
        )

        while True:
            yield self._event(
                state,
                "phase_started",
                phase="reviewing",
                agent=self.critic.name,
            )
            await self.critic.run(state)
            yield self._event(
                state,
                "review_completed",
                review_result=state.review_result,
                critic_feedback=state.critic_feedback,
                quality_score=state.quality_score,
            )

            if state.review_result["verdict"] == "pass":
                break
            if state.iteration >= state.max_iterations:
                break

            state.iteration += 1
            if state.review_result["needs_more_research"]:
                state.pending_search_queries = (
                    state.review_result["search_queries"]
                    or state.review_result["issues"]
                    or state.research_questions
                )
                async for event in self._run_research_phase(
                    state,
                    supplementary=True,
                ):
                    yield event

            # 如果无需新搜索，Writer 根据 review_result 做内容修订；
            # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
            yield self._event(
                state,
                "phase_started",
                phase="writing",
                agent=self.writer.name,
                revision=True,
            )
            await self.writer.run(state)
            yield self._event(
                state,
                "draft_ready",
                report=state.final_report,
                revision=True,
            )

        state.phase = "completed"
        yield self._event(
            state,
            "research_completed",
            report=state.final_report,
            quality_score=state.quality_score,
            references=state.references,
            review_result=state.review_result,
            critic_feedback=state.critic_feedback,
        )

    async def _run_research_phase(
        self,
        state: ResearchState,
        *,
        supplementary: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        """运行搜索和事实提取，并逐步发布研究阶段事件。"""
        yield self._event(
            state,
            "phase_started",
            phase="researching",
            agent=self.researcher.name,
            supplementary=supplementary,
        )
        await self.researcher.run(state)
        await self.fact_extractor.run(state)
        yield self._event(
            state,
            "research_evidence_ready",
            supplementary=supplementary,
            source_count=len(state.raw_sources),
            fact_count=len(state.facts),
            sources=state.raw_sources,
            facts=state.facts,
            references=state.references,
        )

    @staticmethod
    def _event(
        state: ResearchState,
        event_type: str,
        *,
        phase: str | None = None,
        **data: Any,
    ) -> dict[str, Any]:
        """根据当前状态创建一个普通事件字典。"""
        return ResearchEvent(
            type=event_type,
            session_id=state.session_id,
            phase=phase or state.phase,
            iteration=state.iteration,
            data=data,
        ).to_dict()
