"""研究运行和事件的持久化模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


JSON_DATA = JSON().with_variant(JSONB(), "postgresql")


class ResearchRunRecord(Base):
    """一次研究任务的当前快照。"""

    __tablename__ = "research_runs"

    session_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    phase: Mapped[str] = mapped_column(String(40), nullable=False, default="init")
    status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="running", server_default=text("'running'")
    )
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_verdict: Mapped[str | None] = mapped_column(String(40), nullable=True)
    final_report: Mapped[str] = mapped_column(Text, nullable=False, default="")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_data: Mapped[dict[str, Any]] = mapped_column(JSON_DATA, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    events: Mapped[list[ResearchEventRecord]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="ResearchEventRecord.sequence",
    )


class ResearchEventRecord(Base):
    """一次研究事件的不可变记录。"""

    __tablename__ = "research_events"
    __table_args__ = (
        UniqueConstraint("session_id", "sequence", name="uq_research_events_session_sequence"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("research_runs.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    phase: Mapped[str] = mapped_column(String(40), nullable=False)
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data: Mapped[dict[str, Any]] = mapped_column(JSON_DATA, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    run: Mapped[ResearchRunRecord] = relationship(back_populates="events")
