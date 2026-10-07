"""研究任务的 HTTP 和 SSE 接口。"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.graph.runtime import ResearchGraphRuntime

from .dependencies import get_runtime
from .schemas import ResearchRequest


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
