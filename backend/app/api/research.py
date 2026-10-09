"""研究任务的 HTTP 和 SSE 接口。"""

from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.domain.events import RESEARCH_PHASES
from app.graph.runtime import ResearchGraphRuntime
from app.persistence.repository import ResearchRepository

from .dependencies import get_repository, get_run_control, get_runtime
from .schemas import (
    ResearchEventsResponse,
    ResearchRequest,
    ResearchResultResponse,
    RunStatusResponse,
)


router = APIRouter(prefix="/api/research", tags=["research"])


def encode_sse_event(event: dict) -> str:
    """把一个 ResearchEvent 字典编码成标准 SSE 帧。"""

    event_type = str(event.get("type", "message"))
    data = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event_type}\ndata: {data}\n\n"


async def stream_runtime_events(
    runtime: ResearchGraphRuntime,
    query: str,
    session_id: str,
) -> AsyncIterator[str]:
    """把 runtime 的异步事件转换成文本流。"""

    terminal_sent = False
    try:
        async for event in runtime.stream(query, session_id=session_id):
            if isinstance(event, dict):
                yield encode_sse_event(event)
                if event.get("type") in {
                    "research_completed",
                    "research_failed",
                    "research_cancelled",
                }:
                    terminal_sent = True
    except Exception as exc:
        # ResearchGraphRuntime marks the run failed and persists its terminal
        # event before re-raising. Keep the already-started SSE response valid
        # by sending the corresponding terminal frame instead of closing the
        # HTTP body with curl error 18.
        if not terminal_sent:
            yield encode_sse_event(_failure_event(runtime, session_id, exc))


@router.post("/stream")
async def research_stream(
    request: ResearchRequest,
    runtime: ResearchGraphRuntime = Depends(get_runtime),
) -> StreamingResponse:
    """启动研究并按 SSE 推送进度和最终报告。"""

    session_id = request.session_id or str(uuid4())
    return StreamingResponse(
        stream_runtime_events(runtime, request.query, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Research-Session-ID": session_id,
        },
    )


@router.get("/{session_id}/status", response_model=RunStatusResponse)
async def research_status(
    session_id: str,
    run_control=Depends(get_run_control),
    repository: ResearchRepository | None = Depends(get_repository),
) -> RunStatusResponse:
    """优先读取运行控制存储，进程重启后回退到 PostgreSQL 摘要。"""

    status = run_control.get(session_id) if run_control is not None else None
    if status is not None:
        return RunStatusResponse(**status.to_dict())
    if repository is not None:
        persisted_status = repository.load_run_status(session_id)
        if persisted_status is not None:
            return RunStatusResponse(**persisted_status)
    raise HTTPException(status_code=404, detail="研究任务不存在")


@router.post("/{session_id}/cancel", response_model=RunStatusResponse)
async def cancel_research(
    session_id: str,
    run_control=Depends(get_run_control),
) -> RunStatusResponse:
    """请求研究任务在下一个图节点边界停止。"""

    if run_control is None:
        raise HTTPException(status_code=503, detail="运行控制存储未配置")
    if run_control.get(session_id) is None:
        raise HTTPException(status_code=404, detail="研究任务不存在")
    status = run_control.request_cancel(session_id)
    return RunStatusResponse(**status.to_dict())


@router.get("/{session_id}/events", response_model=ResearchEventsResponse)
async def research_events(
    session_id: str,
    repository: ResearchRepository | None = Depends(get_repository),
) -> ResearchEventsResponse:
    """读取 PostgreSQL 中已经保存的研究事件。"""

    if repository is None:
        raise HTTPException(status_code=503, detail="研究 Repository 未配置")
    if repository.load_state(session_id) is None:
        raise HTTPException(status_code=404, detail="研究任务不存在")
    return ResearchEventsResponse(
        session_id=session_id,
        events=repository.list_events(session_id),
    )


@router.get("/{session_id}/result", response_model=ResearchResultResponse)
async def research_result(
    session_id: str,
    repository: ResearchRepository | None = Depends(get_repository),
) -> ResearchResultResponse:
    """读取 PostgreSQL 中保存的最终报告和运行状态。"""

    if repository is None:
        raise HTTPException(status_code=503, detail="研究 Repository 未配置")
    state = repository.load_state(session_id)
    status = repository.load_run_status(session_id)
    if state is None or status is None:
        raise HTTPException(status_code=404, detail="研究任务不存在")
    verdict = state.review_result.get("verdict")
    quality_status = (
        "passed"
        if verdict == "pass"
        else "review_incomplete"
        if verdict in {"needs_revision", "major_issues"}
        else "not_reviewed"
    )
    return ResearchResultResponse(
        session_id=session_id,
        query=state.query,
        status=status["status"],
        phase=status["phase"],
        iteration=status["iteration"],
        error=status["error"],
        final_report=state.final_report,
        quality_status=quality_status,
        quality_gate_passed=verdict == "pass",
        quality_score=state.quality_score,
        unresolved_issues=state.unresolved_issues,
        planner_diagnostics=state.planner_diagnostics,
        updated_at=status["updated_at"],
    )


@router.post("/{session_id}/resume")
async def resume_research(
    session_id: str,
    runtime: ResearchGraphRuntime = Depends(get_runtime),
) -> StreamingResponse:
    """从 LangGraph checkpoint 恢复研究并继续推送 SSE。"""

    if not runtime.can_resume(session_id):
        raise HTTPException(status_code=404, detail="没有可恢复的研究 checkpoint")
    return StreamingResponse(
        stream_runtime_resume_events(runtime, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Research-Session-ID": session_id,
        },
    )


async def stream_runtime_resume_events(
    runtime: ResearchGraphRuntime,
    session_id: str,
) -> AsyncIterator[str]:
    terminal_sent = False
    try:
        async for event in runtime.resume_stream(session_id):
            if isinstance(event, dict):
                yield encode_sse_event(event)
                if event.get("type") in {
                    "research_completed",
                    "research_failed",
                    "research_cancelled",
                }:
                    terminal_sent = True
    except Exception as exc:
        if not terminal_sent:
            yield encode_sse_event(_failure_event(runtime, session_id, exc))


def _failure_event(
    runtime: ResearchGraphRuntime,
    session_id: str,
    error: Exception,
) -> dict:
    """Build a safe failure frame, preferring the runtime's persisted status."""

    status = _runtime_status(runtime, session_id)
    status_error = status.get("error")
    safe_error = _safe_error_text(
        status_error if isinstance(status_error, str) and status_error.strip() else error
    )
    phase = status.get("phase", "init")
    if not isinstance(phase, str) or phase not in RESEARCH_PHASES:
        phase = "init"
    iteration = status.get("iteration", 0)
    if isinstance(iteration, bool) or not isinstance(iteration, int) or iteration < 0:
        iteration = 0
    return {
        "type": "research_failed",
        "session_id": session_id,
        "phase": phase,
        "iteration": iteration,
        "error": safe_error,
    }


def _runtime_status(runtime: ResearchGraphRuntime, session_id: str) -> dict:
    """Read a runtime status without allowing a secondary lookup failure to mask SSE."""

    get_status = getattr(runtime, "get_run_status", None)
    if not callable(get_status):
        return {}
    try:
        status = get_status(session_id)
    except Exception:
        return {}
    if status is None:
        return {}
    if isinstance(status, dict):
        return status
    to_dict = getattr(status, "to_dict", None)
    if callable(to_dict):
        try:
            value = to_dict()
        except Exception:
            return {}
        return value if isinstance(value, dict) else {}
    return {
        "phase": getattr(status, "phase", None),
        "iteration": getattr(status, "iteration", None),
        "error": getattr(status, "error", None),
    }


def _safe_error_text(error: object) -> str:
    """Return a one-line error without common credential formats or tracebacks."""

    safe_message = getattr(error, "safe_message", None)
    value = (
        safe_message
        if isinstance(safe_message, str) and safe_message.strip()
        else str(error)
    )
    value = value.splitlines()[0] if value.splitlines() else ""
    value = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", value)
    value = re.sub(
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", value
    )
    value = re.sub(r"(?i)\b(?:sk|rk)-[A-Za-z0-9_-]{12,}", "[REDACTED]", value)
    value = re.sub(
        r"(?i)\b(api[_ -]?key|access[_ -]?token|refresh[_ -]?token|password|secret|authorization)"
        r"\s*[:=]\s*[^\s,;]+",
        r"\1=[REDACTED]",
        value,
    )
    value = " ".join(value.split())[:1000]
    return value or "研究执行失败，请通过任务状态接口查看诊断信息。"
