"""LangGraph 唯一的 V2 运行入口。

这里负责组装 Agent、编译图和把图事件转成对外事件。流程顺序和审核
分支全部定义在 ``research_graph.py``，不再由单独的 ResearchWorkflow
类维护第二套编排逻辑。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
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
from app.persistence.repository import ResearchRepository

from .nodes import ResearchGraphNodes
from .research_graph import build_research_graph
from .state import initial_graph_state


@dataclass(frozen=True)
class ResearchGraphRuntime:
    """一次 LangGraph 运行所需的已编译图和配置。"""

    graph: Any
    max_iterations: int = 1
    repository: ResearchRepository | None = None

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        state = self._new_state(query, session_id)
        if self.repository is not None:
            self.repository.save_state(state)
        latest_state = state
        async for node_update in self._stream_updates(state):
            latest_state = self._persist_update(node_update, latest_state)
        return latest_state

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        state = self._new_state(query, session_id)
        if self.repository is not None:
            self.repository.save_state(state)
        async for node_update in self._stream_updates(state):
            self._persist_update(node_update, state)
            events = node_update.get("events", [])
            if isinstance(events, list):
                async for event in from_events(events):
                    yield event

    async def _stream_updates(
        self,
        state: ResearchState,
    ) -> AsyncIterator[dict[str, Any]]:
        async for update in self.graph.astream(
            initial_graph_state(state),
            config=self._graph_config(),
            stream_mode="updates",
        ):
            if not isinstance(update, dict):
                continue
            for node_update in update.values():
                if isinstance(node_update, dict):
                    yield node_update

    def _persist_update(
        self,
        node_update: dict[str, Any],
        latest_state: ResearchState,
    ) -> ResearchState:
        state = node_update.get("research_state", latest_state)
        if isinstance(state, ResearchState):
            latest_state = state
            if self.repository is not None:
                self.repository.save_state(state)
        events = node_update.get("events", [])
        if self.repository is not None and isinstance(events, list):
            self.repository.append_events(
                event for event in events if isinstance(event, dict)
            )
        return latest_state

    def _new_state(self, query: str, session_id: str | None) -> ResearchState:
        return ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
            max_iterations=self.max_iterations,
        )

    def _graph_config(self) -> dict[str, int]:
        return {"recursion_limit": max(30, 20 + 12 * self.max_iterations)}


def from_events(events: list[Any]) -> AsyncIterator[dict[str, Any]]:
    """把一个图节点的事件列表转成异步事件流。"""

    async def iterator() -> AsyncIterator[dict[str, Any]]:
        for event in events:
            if isinstance(event, dict):
                yield event

    return iterator()


def create_research_runtime(
    llm: LLMClient,
    search: SearchClient,
    *,
    results_per_question: int = 3,
    max_iterations: int = 1,
    repository: ResearchRepository | None = None,
) -> ResearchGraphRuntime:
    """创建唯一的 V2 LangGraph 运行实例。"""

    if max_iterations < 0:
        raise ValueError("max_iterations 不能小于 0")
    nodes = ResearchGraphNodes(
        planner=PlannerAgent(llm),
        researcher=ResearcherAgent(search, results_per_question),
        fact_extractor=FactExtractorAgent(llm),
        data_analyst=DataAnalystAgent(llm),
        code_wizard=CodeWizardAgent(llm),
        writer=WriterAgent(llm),
        critic=CriticAgent(llm),
    )
    return ResearchGraphRuntime(
        graph=build_research_graph(nodes),
        max_iterations=max_iterations,
        repository=repository,
    )
