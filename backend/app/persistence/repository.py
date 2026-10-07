"""研究运行和事件的数据库访问层。"""

from __future__ import annotations

from dataclasses import fields
from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.state import ResearchState

from .models import ResearchEventRecord, ResearchRunRecord
from .serialization import event_to_record, state_to_dict


class ResearchRepository:
    """只负责 PostgreSQL/SQLAlchemy 数据访问，不参与 Agent 编排。"""

    def __init__(self, session: Session):
        self.session = session

    def save_state(self, state: ResearchState) -> ResearchRunRecord:
        """创建或更新一次研究任务的最新状态快照。"""

        payload = state_to_dict(state)
        record = self.session.get(ResearchRunRecord, state.session_id)
        if record is None:
            record = ResearchRunRecord(session_id=state.session_id)
            self.session.add(record)

        record.query = state.query
        record.phase = state.phase
        record.iteration = state.iteration
        record.max_iterations = state.max_iterations
        record.quality_score = state.quality_score
        record.review_verdict = state.review_result.get("verdict")
        record.final_report = state.final_report
        record.state_data = payload
        self.session.commit()
        self.session.refresh(record)
        return record

    def append_event(
        self,
        event: dict[str, Any],
        *,
        sequence: int | None = None,
    ) -> ResearchEventRecord:
        """按会话追加一个不可变事件，并自动计算顺序号。"""

        values = event_to_record(event)
        session_id = values["session_id"]
        if self.session.get(ResearchRunRecord, session_id) is None:
            raise ValueError(f"研究任务不存在: {session_id}")

        if sequence is None:
            latest = self.session.scalar(
                select(func.max(ResearchEventRecord.sequence)).where(
                    ResearchEventRecord.session_id == session_id
                )
            )
            sequence = 0 if latest is None else int(latest) + 1
        if sequence < 0:
            raise ValueError("事件 sequence 不能小于 0")

        values["sequence"] = sequence
        record = ResearchEventRecord(**values)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def append_events(
        self,
        events: Iterable[dict[str, Any]],
    ) -> list[ResearchEventRecord]:
        """按传入顺序批量追加事件。"""

        records = []
        for event in events:
            records.append(self.append_event(event))
        return records

    def load_state(self, session_id: str) -> ResearchState | None:
        """读取最新领域状态；不存在时返回 None。"""

        record = self.session.get(ResearchRunRecord, session_id)
        if record is None:
            return None
        state_fields = {field.name for field in fields(ResearchState)}
        payload = {
            key: value for key, value in (record.state_data or {}).items() if key in state_fields
        }
        payload.setdefault("query", record.query)
        payload.setdefault("session_id", record.session_id)
        return ResearchState(**payload)

    def list_events(self, session_id: str) -> list[dict[str, Any]]:
        """按 sequence 返回扁平化的 ResearchEvent 字典。"""

        records = self.session.scalars(
            select(ResearchEventRecord)
            .where(ResearchEventRecord.session_id == session_id)
            .order_by(ResearchEventRecord.sequence)
        ).all()
        return [
            {
                "type": record.event_type,
                "session_id": record.session_id,
                "phase": record.phase,
                "iteration": record.iteration,
                **(record.data or {}),
            }
            for record in records
        ]
