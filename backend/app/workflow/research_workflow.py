"""DeepResearch 的公开工作流接口。

I7 开始由 LangGraph 负责节点编排。本文件保留学习版原来的 ``run`` 和
``stream`` 调用方式，并把 LangGraph 的节点更新转换成稳定的研究事件。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.agents.code_wizard import CodeWizardAgent
from app.agents.critic import CriticAgent
from app.agents.data_analyst import DataAnalystAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
from app.domain.state import ResearchState
from app.graph.nodes import ResearchGraphNodes
from app.graph.research_graph import build_research_graph
from app.graph.state import initial_graph_state


class ResearchWorkflow:
    """V2 研究图的稳定外壳。

    Agent 实例仍由这里创建，业务状态仍是 ``ResearchState``；LangGraph
    只负责调度节点和审核后的条件分支。
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
        self.data_analyst = DataAnalystAgent(llm)
        self.code_wizard = CodeWizardAgent(llm)
        self.writer = WriterAgent(llm)
        self.critic = CriticAgent(llm)
        self.graph_nodes = ResearchGraphNodes(
            planner=self.planner,
            researcher=self.researcher,
            fact_extractor=self.fact_extractor,
            data_analyst=self.data_analyst,
            code_wizard=self.code_wizard,
            writer=self.writer,
            critic=self.critic,
        )
        self.graph = build_research_graph(self.graph_nodes)

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        """执行一次完整研究并返回最终状态。"""

        state = self._new_state(query, session_id)
        result = await self.graph.ainvoke(
            initial_graph_state(state),
            config=self._graph_config(),
        )
        return result["research_state"]

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """逐步发布稳定研究事件，不暴露 LangGraph 内部更新格式。"""

        state = self._new_state(query, session_id)
        async for event in self._stream_state(state):
            yield event

    def _new_state(
        self,
        query: str,
        session_id: str | None,
    ) -> ResearchState:
        """创建一次研究任务的初始领域状态。"""

        return ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
            max_iterations=self.max_iterations,
        )

    async def _stream_state(
        self,
        state: ResearchState,
    ) -> AsyncIterator[dict[str, Any]]:
        """运行 LangGraph，并只转发节点产生的业务事件。"""

        graph_input = initial_graph_state(state)
        async for update in self.graph.astream(
            graph_input,
            config=self._graph_config(),
            stream_mode="updates",
        ):
            if not isinstance(update, dict):
                continue
            for node_update in update.values():
                if not isinstance(node_update, dict):
                    continue
                events = node_update.get("events", [])
                if isinstance(events, list):
                    for event in events:
                        if isinstance(event, dict):
                            yield event

    def _graph_config(self) -> dict[str, int]:
        """允许每次审核修订循环完成，同时仍限制意外的无限循环。"""

        return {"recursion_limit": max(25, 12 + 8 * self.max_iterations)}
