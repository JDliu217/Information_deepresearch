"""API 请求和响应模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """启动一次研究所需的输入。"""

    query: str = Field(min_length=1, description="研究问题")
    session_id: str | None = Field(default=None, min_length=1)

    @field_validator("query")
    @classmethod
    def reject_query_replaced_by_question_marks(cls, value: str) -> str:
        """Fail early when a terminal encoding replaced most query text."""

        query = value.strip()
        replacement_characters = sum(
            character in {"?", "？", "\ufffd"} for character in query
        )
        if (
            replacement_characters >= 3
            and replacement_characters / max(len(query), 1) >= 0.5
        ):
            raise ValueError(
                "研究问题包含过多问号或替换字符，可能是终端编码错误；请使用 UTF-8 重新发送。"
            )
        return value


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
