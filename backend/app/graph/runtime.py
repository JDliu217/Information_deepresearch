"""LangGraph 唯一的 V2 运行入口。

这里负责组装 Agent、编译图和把图事件转成对外事件。流程顺序和审核
分支全部定义在 ``research_graph.py``，不再由单独的 ResearchWorkflow
类维护第二套编排逻辑。
"""

from __future__ import annotations

import asyncio
import logging
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


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResearchGraphRuntime:
    """一次 LangGraph 运行所需的已编译图和配置。"""

    graph: Any
    max_iterations: int = 3
    repository: ResearchRepository | None = None
    run_control: RunControlStore | None = None

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        state = self._new_state(query, session_id)
        return await self._run_state(state, resume=False)

    async def resume(self, session_id: str) -> ResearchState:
        """从指定 session 的 LangGraph checkpoint 继续运行。"""

        state = self._load_checkpoint(session_id)
        return await self._run_state(state, resume=True)

    async def _run_state(self, state: ResearchState, *, resume: bool) -> ResearchState:
        latest_state = state
        try:
            self._start_run(state)
            if self.repository is not None:
                self.repository.save_state(state, status="running", error=None)
            async for node_update in self._stream_updates(state, resume=resume):
                latest_state = self._persist_update(node_update, latest_state)
                self._update_run_status(latest_state, node_update.get("events", []))
                if node_update.get("_cancelled_boundary"):
                    if node_update.get("_node_name") and getattr(self.graph, "checkpointer", None):
                        await self._restore_checkpoint_after_cancel(
                            latest_state.session_id,
                            latest_state,
                            node_update["_node_name"],
                        )
                    self._mark_cancelled(latest_state)
                    return latest_state
            self._mark_completed(latest_state)
            return latest_state
        except Exception as exc:
            failure_state = getattr(exc, "research_state", latest_state)
            if isinstance(failure_state, ResearchState):
                latest_state = failure_state
            self._mark_failed(latest_state, exc)
            raise

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        state = self._new_state(query, session_id)
        async for event in self._stream_state_events(state, resume=False):
            yield event

    async def resume_stream(self, session_id: str) -> AsyncIterator[dict[str, Any]]:
        """从 checkpoint 恢复并按事件流输出。"""

        state = self._load_checkpoint(session_id)
        async for event in self._stream_state_events(state, resume=True):
            yield event

    async def _stream_state_events(
        self,
        state: ResearchState,
        *,
        resume: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        try:
            self._start_run(state)
            if self.repository is not None:
                self.repository.save_state(state, status="running", error=None)
            async for node_update in self._stream_updates(state, resume=resume):
                state = self._persist_update(node_update, state)
                events = node_update.get("events", [])
                if isinstance(events, list):
                    async for event in from_events(events):
                        yield event
                self._update_run_status(state, node_update.get("events", []))
                if node_update.get("_cancelled_boundary"):
                    if node_update.get("_node_name") and getattr(self.graph, "checkpointer", None):
                        await self._restore_checkpoint_after_cancel(
                            state.session_id,
                            state,
                            node_update["_node_name"],
                        )
                    self._mark_cancelled(state)
                    # LangGraph schedules the checkpoint write immediately
                    # before publishing an update. Give that task one event
                    # loop turn to finish before closing ``astream``.
                    await asyncio.sleep(0.01)
                    return
            self._mark_completed(state)
        except Exception as exc:
            failure_state = getattr(exc, "research_state", state)
            if isinstance(failure_state, ResearchState):
                state = failure_state
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

    def can_resume(self, session_id: str) -> bool:
        """判断当前图是否有可读取的 checkpoint。"""

        try:
            snapshot = self.graph.get_state(self._graph_config(session_id))
        except (AttributeError, ValueError):
            return False
        return bool(snapshot and snapshot.values and snapshot.next)

    def _load_checkpoint(self, session_id: str) -> ResearchState:
        if not self.can_resume(session_id):
            raise ValueError(f"没有可恢复的研究 checkpoint: {session_id}")
        snapshot = self.graph.get_state(self._graph_config(session_id))
        state = snapshot.values.get("research_state")
        if not isinstance(state, ResearchState):
            raise ValueError(f"checkpoint 缺少研究状态: {session_id}")
        return state

    async def _stream_updates(
        self,
        state: ResearchState,
        *,
        resume: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        graph_stream = self.graph.astream(
            None if resume else initial_graph_state(state),
            config=self._graph_config(state.session_id),
            stream_mode=["updates", "custom"],
        )
        cancellation_probe = False
        close_stream = True
        try:
            while True:
                if self._should_cancel(state):
                    cancellation_probe = True
                try:
                    update = await graph_stream.__anext__()
                except StopAsyncIteration:
                    if cancellation_probe:
                        yield {"events": [], "_cancelled_boundary": True}
                    return
                if isinstance(update, tuple) and len(update) in {2, 3}:
                    mode, payload = (
                        update[-2],
                        update[-1],
                    )
                    if mode == "custom" and isinstance(payload, dict):
                        node_update = {"events": [payload], "_custom_stream": True}
                        yield node_update
                    elif mode == "updates" and isinstance(payload, dict):
                        for node_name, node_update in payload.items():
                            if isinstance(node_update, dict):
                                node_update = dict(node_update)
                                node_update["_node_boundary"] = True
                                node_update["_node_name"] = node_name
                                if cancellation_probe:
                                    node_update["_cancelled_boundary"] = True
                                yield node_update
                                if node_update.get("_cancelled_boundary"):
                                    close_stream = False
                                    return
                elif isinstance(update, dict):
                    # Compatibility with LangGraph versions/configurations
                    # that return a plain update mapping for a single mode.
                    for node_update in update.values():
                        if isinstance(node_update, dict):
                            node_update = dict(node_update)
                            if cancellation_probe:
                                node_update["_cancelled_boundary"] = True
                            yield node_update
                            if cancellation_probe:
                                close_stream = False
                                return
        finally:
            if close_stream:
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

    def _update_run_status(self, state: ResearchState, events: Any = None) -> None:
        if self.run_control is not None:
            phase = state.phase
            if isinstance(events, list):
                for event in events:
                    if isinstance(event, dict) and event.get("phase"):
                        phase = str(event["phase"])
            self.run_control.update(
                state.session_id,
                phase=phase,
                iteration=state.iteration,
            )

    def _mark_completed(self, state: ResearchState) -> None:
        if self.repository is not None:
            self.repository.save_state(state, status="completed", error=None)
        if self.run_control is not None:
            self.run_control.mark_completed(
                state.session_id,
                phase=state.phase,
                iteration=state.iteration,
            )

    def _mark_cancelled(self, state: ResearchState) -> None:
        if self.repository is not None:
            self.repository.save_state(state, status="cancelled", error=None)
            self.repository.append_event(
                {
                    "type": "research_cancelled",
                    "session_id": state.session_id,
                    "phase": state.phase,
                    "iteration": state.iteration,
                    "reason": "cancelled at graph node boundary",
                }
            )
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
        if self.repository is not None:
            try:
                self.repository.save_state(
                    state,
                    status="failed",
                    error=str(error),
                )
                self.repository.append_event(
                    {
                        "type": "research_failed",
                        "session_id": state.session_id,
                        "phase": state.phase,
                        "iteration": state.iteration,
                        "error": str(error),
                        **(
                            {"planner_diagnostics": error.diagnostics}
                            if isinstance(getattr(error, "diagnostics", None), list)
                            else {}
                        ),
                    }
                )
            except Exception:
                logger.exception(
                    "Failed to persist failure details for research session %s",
                    state.session_id,
                )

    async def _restore_checkpoint_after_cancel(
        self,
        session_id: str,
        state: ResearchState,
        node_name: str,
    ) -> None:
        """Reopen the successor edge after an interrupted async stream."""

        await self.graph.aupdate_state(
            self._graph_config(session_id),
            {"research_state": state},
            as_node=node_name,
        )

    def _graph_config(self, session_id: str | None = None) -> dict[str, Any]:
        config: dict[str, Any] = {
            "recursion_limit": max(80, 40 + 20 * self.max_iterations),
        }
        if session_id:
            config["configurable"] = {"thread_id": session_id}
        return config



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
    results_per_question: int = 10,
    max_iterations: int = 3,
    repository: ResearchRepository | None = None,
    run_control: RunControlStore | None = None,
    checkpointer: Any | None = None,
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
        graph=build_research_graph(nodes, checkpointer=checkpointer),
        max_iterations=max_iterations,
        repository=repository,
        run_control=run_control,
    )
