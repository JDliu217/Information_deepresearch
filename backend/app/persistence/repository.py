"""研究运行和事件的数据库访问层。"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import fields
from typing import Any, Iterable, Iterator

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.state import ResearchState

from .models import ResearchEventRecord, ResearchRunRecord
from .serialization import event_to_record, state_to_dict


_UNSET = object()


class ResearchRepository:
    """只负责 PostgreSQL/SQLAlchemy 数据访问，不参与 Agent 编排。

    可以接收单个 ``Session``（适用于测试或短生命周期任务），也可以接收
    ``sessionmaker``，让每次数据库操作使用独立 Session，适合 FastAPI 并发请求。
    """

    def __init__(
        self,
        session: Session | sessionmaker[Session],
        *,
        engine: Engine | None = None,
        owns_engine: bool = False,
    ):
        if isinstance(session, Session):
            self.session: Session | None = session
            self._session_factory: sessionmaker[Session] | None = None
            bound_engine = session.get_bind()
        else:
            self.session = None
            self._session_factory = session
            bound_engine = getattr(session, "kw", {}).get("bind")

        self.engine = engine or bound_engine
        self.owns_engine = owns_engine

    @contextmanager
    def _session_scope(self) -> Iterator[Session]:
        if self.session is not None:
            yield self.session
            return
        if self._session_factory is None:
            raise RuntimeError("ResearchRepository 没有可用的 SQLAlchemy Session")
        with self._session_factory() as session:
            yield session

    def close(self) -> None:
        """释放由 Repository 工厂创建并持有的 Engine。"""

        if self.owns_engine and self.engine is not None:
            self.engine.dispose()

    def save_state(
        self,
        state: ResearchState,
        *,
        status: str | None = None,
        error: Any = _UNSET,
    ) -> ResearchRunRecord:
        """创建或更新一次研究任务的最新状态快照。"""

        payload = state_to_dict(state)
        with self._session_scope() as session:
            record = session.get(ResearchRunRecord, state.session_id)
            is_new = record is None
            if record is None:
                record = ResearchRunRecord(session_id=state.session_id)
                session.add(record)

            record.query = state.query
            record.phase = state.phase
            record.iteration = state.iteration
            record.max_iterations = state.max_iterations
            record.quality_score = state.quality_score
            record.review_verdict = state.review_result.get("verdict")
            record.final_report = state.final_report
            record.state_data = payload
            if status is not None:
                record.status = status
            elif is_new:
                record.status = "completed" if state.phase == "completed" else "running"
            if error is not _UNSET:
                record.error = error

            session.commit()
            session.refresh(record)
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
        with self._session_scope() as session:
            run = session.get(ResearchRunRecord, session_id)
            if run is None:
                raise ValueError(f"研究任务不存在: {session_id}")

            if sequence is None:
                latest = session.scalar(
                    select(func.max(ResearchEventRecord.sequence)).where(
                        ResearchEventRecord.session_id == session_id
                    )
                )
                sequence = 0 if latest is None else int(latest) + 1
            if sequence < 0:
                raise ValueError("事件 sequence 不能小于 0")

            values["sequence"] = sequence
            record = ResearchEventRecord(**values)
            session.add(record)
            self._update_run_from_event(run, event)
            session.commit()
            session.refresh(record)
            return record

    def append_events(
        self,
        events: Iterable[dict[str, Any]],
    ) -> list[ResearchEventRecord]:
        """按传入顺序追加事件。"""

        return [self.append_event(event) for event in events]

    def load_state(self, session_id: str) -> ResearchState | None:
        """读取最新领域状态；不存在时返回 None。"""

        with self._session_scope() as session:
            record = session.get(ResearchRunRecord, session_id)
            if record is None:
                return None
            state_fields = {field.name for field in fields(ResearchState)}
            payload = {
                key: value
                for key, value in (record.state_data or {}).items()
                if key in state_fields
            }
            payload.setdefault("query", record.query)
            payload.setdefault("session_id", record.session_id)
            return ResearchState(**payload)

    def load_run_status(self, session_id: str) -> dict[str, Any] | None:
        """读取数据库中持久化的运行摘要，可供进程重启后查询。"""

        with self._session_scope() as session:
            record = session.get(ResearchRunRecord, session_id)
            if record is None:
                return None
            return {
                "session_id": record.session_id,
                "status": record.status,
                "phase": record.phase,
                "iteration": record.iteration,
                "error": record.error,
                "updated_at": record.updated_at.isoformat(),
            }

    def list_events(self, session_id: str) -> list[dict[str, Any]]:
        """按 sequence 返回含数据库时间戳的 ResearchEvent 字典。"""

        with self._session_scope() as session:
            records = session.scalars(
                select(ResearchEventRecord)
                .where(ResearchEventRecord.session_id == session_id)
                .order_by(ResearchEventRecord.sequence)
            ).all()
            return [
                {
                    "type": record.event_type,
                    "session_id": record.session_id,
                    "sequence": record.sequence,
                    "phase": record.phase,
                    "iteration": record.iteration,
                    "created_at": record.created_at.isoformat(),
                    **(record.data or {}),
                }
                for record in records
            ]

    @staticmethod
    def _update_run_from_event(run: ResearchRunRecord, event: dict[str, Any]) -> None:
        run.phase = str(event["phase"])
        run.iteration = int(event["iteration"])
        event_type = event["type"]
        if event_type == "research_started":
            run.status = "running"
            run.error = None
        elif event_type == "research_completed":
            run.status = "completed"
            run.error = None
        elif event_type == "research_failed":
            run.status = "failed"
            run.error = str(event.get("error") or "研究运行失败")
        elif event_type == "research_cancelled":
            run.status = "cancelled"
