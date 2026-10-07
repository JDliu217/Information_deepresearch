"""研究任务的 HTTP 和 SSE 接口。"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.graph.runtime import ResearchGraphRuntime
from app.persistence.repository import ResearchRepository

from .dependencies import get_repository, get_run_control, get_runtime
from .schemas import ResearchEventsResponse, ResearchRequest, RunStatusResponse


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

    async for event in runtime.stream(query, session_id=session_id):
        if isinstance(event, dict):
            yield encode_sse_event(event)


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
) -> RunStatusResponse:
    """读取 Redis 或内存中的运行摘要。"""

    if run_control is None:
        raise HTTPException(status_code=503, detail="运行控制存储未配置")
    status = run_control.get(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="研究任务不存在")
    return RunStatusResponse(**status.to_dict())


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
    async for event in runtime.resume_stream(session_id):
        if isinstance(event, dict):
            yield encode_sse_event(event)
