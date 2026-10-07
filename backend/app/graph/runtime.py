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
from app.core.run_control import RunControlStore
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
    run_control: RunControlStore | None = None

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        state = self._new_state(query, session_id)
        self._start_run(state)
        if self.repository is not None:
            self.repository.save_state(state)
        latest_state = state
        try:
            async for node_update in self._stream_updates(state):
                latest_state = self._persist_update(node_update, latest_state)
                if self._should_cancel(latest_state):
                    self._mark_cancelled(latest_state)
                    return latest_state
                self._update_run_status(latest_state)
            self._mark_completed(latest_state)
            return latest_state
        except Exception as exc:
            self._mark_failed(latest_state, exc)
            raise

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        state = self._new_state(query, session_id)
        self._start_run(state)
        if self.repository is not None:
            self.repository.save_state(state)
        try:
            async for node_update in self._stream_updates(state):
                state = self._persist_update(node_update, state)
                events = node_update.get("events", [])
                if isinstance(events, list):
                    async for event in from_events(events):
                        yield event
                if self._should_cancel(state):
                    self._mark_cancelled(state)
                    return
                self._update_run_status(state)
            self._mark_completed(state)
        except Exception as exc:
            self._mark_failed(state, exc)
            raise

    def request_cancel(self, session_id: str):
        """设置取消标志；实际停止发生在下一个图节点边界。"""

        if self.run_control is None:
            raise RuntimeError("当前 runtime 没有配置运行控制存储")
        return self.run_control.request_cancel(session_id)

    def get_run_status(self, session_id: str):
        """读取运行摘要，供后续 API 或 SSE 查询。"""

        if self.run_control is None:
            return None
        return self.run_control.get(session_id)

    async def _stream_updates(
        self,
        state: ResearchState,
    ) -> AsyncIterator[dict[str, Any]]:
        graph_stream = self.graph.astream(
            initial_graph_state(state),
            config=self._graph_config(),
            stream_mode="updates",
        )
        try:
            while True:
                if self._should_cancel(state):
                    return
                try:
                    update = await graph_stream.__anext__()
                except StopAsyncIteration:
                    return
                if not isinstance(update, dict):
                    continue
                for node_update in update.values():
                    if isinstance(node_update, dict):
                        yield node_update
        finally:
            await graph_stream.aclose()

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

    def _start_run(self, state: ResearchState) -> None:
        if self.run_control is not None:
            self.run_control.start(state.session_id)

    def _should_cancel(self, state: ResearchState) -> bool:
        return (
            state.phase != "completed"
            and self.run_control is not None
            and self.run_control.is_cancel_requested(state.session_id)
        )

    def _update_run_status(self, state: ResearchState) -> None:
        if self.run_control is not None:
            self.run_control.update(
                state.session_id,
                phase=state.phase,
                iteration=state.iteration,
            )

    def _mark_completed(self, state: ResearchState) -> None:
        if self.run_control is not None:
            self.run_control.mark_completed(
                state.session_id,
                phase=state.phase,
                iteration=state.iteration,
            )

    def _mark_cancelled(self, state: ResearchState) -> None:
        if self.run_control is not None:
            self.run_control.mark_cancelled(
                state.session_id,
                phase=state.phase,
                iteration=state.iteration,
            )

    def _mark_failed(self, state: ResearchState, error: Exception) -> None:
        if self.run_control is not None:
            self.run_control.mark_failed(
                state.session_id,
                phase=state.phase,
                iteration=state.iteration,
                error=str(error),
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
    run_control: RunControlStore | None = None,
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
        run_control=run_control,
    )
