"""把多个 Agent 编排成一次完整研究任务。"""

from __future__ import annotations

from uuid import uuid4

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
from app.domain.state import ResearchState


class ResearchWorkflow:
    """Iteration 01 的最小同步编排器。

    每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
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
        state = ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
            max_iterations=self.max_iterations,
        )

        await self.planner.run(state)
        await self.researcher.run(state)
        await self.fact_extractor.run(state)
        await self.writer.run(state)

        while True:
            await self.critic.run(state)
            if state.review["verdict"] == "pass":
                break
            if state.iteration >= state.max_iterations:
                break

            state.iteration += 1
            if state.review["needs_more_research"]:
                state.pending_search_queries = (
                    state.review["search_queries"]
                    or state.review["issues"]
                    or state.research_questions
                )
                await self.researcher.run(state)
                await self.fact_extractor.run(state)

            # 如果无需新搜索，Writer 根据 state.review 做内容修订；
            # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
            await self.writer.run(state)

        state.phase = "completed"
        return state
