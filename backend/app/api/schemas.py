"""API 请求和响应模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """启动一次研究所需的输入。"""

    query: str = Field(min_length=1, description="研究问题")
    session_id: str | None = Field(default=None, min_length=1)


class HealthResponse(BaseModel):
    status: str


class RunStatusResponse(BaseModel):
    session_id: str
    status: str
    phase: str
    iteration: int
    error: str | None = None
    updated_at: str


class ResearchEventsResponse(BaseModel):
    session_id: str
    events: list[dict]
