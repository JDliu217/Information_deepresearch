"""研究任务的短期运行状态和取消控制。

PostgreSQL 保存完整研究结果；本模块只保存运行中的轻量状态，方便后续
SSE 查询进度和请求取消。runtime 依赖协议，不直接依赖 Redis。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Protocol


RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
CANCEL_REQUESTED = "cancel_requested"
CANCELLED = "cancelled"
RUN_STATUSES = frozenset(
    {RUNNING, COMPLETED, FAILED, CANCEL_REQUESTED, CANCELLED}
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RunStatus:
    """Redis 中保存的一次研究运行摘要。"""

    session_id: str
    status: str = RUNNING
    phase: str = "init"
    iteration: int = 0
    error: str | None = None
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.session_id.strip():
            raise ValueError("运行状态 session_id 不能为空")
        if self.status not in RUN_STATUSES:
            raise ValueError(f"不支持的运行状态: {self.status!r}")
        if self.iteration < 0:
            raise ValueError("运行状态 iteration 不能小于 0")
        if not self.updated_at:
            object.__setattr__(self, "updated_at", _timestamp())

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self.status,
            "phase": self.phase,
            "iteration": self.iteration,
            "error": self.error,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunStatus":
        return cls(
            session_id=str(payload["session_id"]),
            status=str(payload.get("status", RUNNING)),
            phase=str(payload.get("phase", "init")),
            iteration=int(payload.get("iteration", 0)),
            error=payload.get("error"),
            updated_at=str(payload.get("updated_at", "")),
        )


class RunControlStore(Protocol):
    """runtime 所需的运行状态和取消操作。"""

    def start(self, session_id: str) -> RunStatus:
        ...

    def update(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        ...

    def mark_completed(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        ...

    def mark_failed(self, session_id: str, *, phase: str, iteration: int, error: str) -> RunStatus:
        ...

    def mark_cancelled(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        ...

    def request_cancel(self, session_id: str) -> RunStatus:
        ...

    def is_cancel_requested(self, session_id: str) -> bool:
        ...

    def get(self, session_id: str) -> RunStatus | None:
        ...


class InMemoryRunControlStore:
    """测试和本地学习使用的运行控制实现。"""

    def __init__(self) -> None:
        self._statuses: dict[str, RunStatus] = {}
        self._cancelled: set[str] = set()

    def start(self, session_id: str) -> RunStatus:
        self._cancelled.discard(session_id)
        return self._save(RunStatus(session_id=session_id, status=RUNNING))

    def update(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        return self._save(
            RunStatus(session_id=session_id, status=RUNNING, phase=phase, iteration=iteration)
        )

    def mark_completed(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        self._cancelled.discard(session_id)
        return self._save(
            RunStatus(session_id=session_id, status=COMPLETED, phase=phase, iteration=iteration)
        )

    def mark_failed(self, session_id: str, *, phase: str, iteration: int, error: str) -> RunStatus:
        self._cancelled.discard(session_id)
        return self._save(
            RunStatus(
                session_id=session_id,
                status=FAILED,
                phase=phase,
                iteration=iteration,
                error=error,
            )
        )

    def mark_cancelled(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        self._cancelled.discard(session_id)
        return self._save(
            RunStatus(session_id=session_id, status=CANCELLED, phase=phase, iteration=iteration)
        )

    def request_cancel(self, session_id: str) -> RunStatus:
        current = self.get(session_id) or RunStatus(session_id=session_id)
        if current.status in {COMPLETED, FAILED, CANCELLED}:
            return current
        self._cancelled.add(session_id)
        return self._save(replace(current, status=CANCEL_REQUESTED, updated_at=_timestamp()))

    def is_cancel_requested(self, session_id: str) -> bool:
        return session_id in self._cancelled

    def get(self, session_id: str) -> RunStatus | None:
        return self._statuses.get(session_id)

    def _save(self, status: RunStatus) -> RunStatus:
        self._statuses[status.session_id] = status
        return status


class RedisRunControlStore:
    """Redis-backed implementation used by deployed workers."""

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        *,
        key_prefix: str = "information_deepresearch:",
        ttl_seconds: int = 86_400,
        client: Any | None = None,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds 必须大于 0")
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds
        if client is None:
            try:
                from redis import Redis
            except ImportError as exc:
                raise RuntimeError("使用 RedisRunControlStore 前请安装 redis 依赖") from exc
            client = Redis.from_url(url, decode_responses=True)
        self.client = client

    def start(self, session_id: str) -> RunStatus:
        self._delete(self._cancel_key(session_id))
        return self._save(RunStatus(session_id=session_id, status=RUNNING))

    def update(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        return self._save(
            RunStatus(session_id=session_id, status=RUNNING, phase=phase, iteration=iteration)
        )

    def mark_completed(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        self._delete(self._cancel_key(session_id))
        return self._save(
            RunStatus(session_id=session_id, status=COMPLETED, phase=phase, iteration=iteration)
        )

    def mark_failed(self, session_id: str, *, phase: str, iteration: int, error: str) -> RunStatus:
        self._delete(self._cancel_key(session_id))
        return self._save(
            RunStatus(
                session_id=session_id,
                status=FAILED,
                phase=phase,
                iteration=iteration,
                error=error,
            )
        )

    def mark_cancelled(self, session_id: str, *, phase: str, iteration: int) -> RunStatus:
        self._delete(self._cancel_key(session_id))
        return self._save(
            RunStatus(session_id=session_id, status=CANCELLED, phase=phase, iteration=iteration)
        )

    def request_cancel(self, session_id: str) -> RunStatus:
        current = self.get(session_id) or RunStatus(session_id=session_id)
        if current.status in {COMPLETED, FAILED, CANCELLED}:
            return current
        self._set(self._cancel_key(session_id), "1")
        return self._save(replace(current, status=CANCEL_REQUESTED, updated_at=_timestamp()))

    def is_cancel_requested(self, session_id: str) -> bool:
        return bool(self.client.exists(self._cancel_key(session_id)))

    def get(self, session_id: str) -> RunStatus | None:
        value = self.client.get(self._status_key(session_id))
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return RunStatus.from_dict(json.loads(value))

    def _save(self, status: RunStatus) -> RunStatus:
        self._set(self._status_key(status.session_id), json.dumps(status.to_dict()))
        return status

    def _set(self, key: str, value: str) -> None:
        self.client.set(key, value, ex=self.ttl_seconds)

    def _delete(self, key: str) -> None:
        self.client.delete(key)

    def _status_key(self, session_id: str) -> str:
        return f"{self.key_prefix}run:{session_id}:status"

    def _cancel_key(self, session_id: str) -> str:
        return f"{self.key_prefix}run:{session_id}:cancel"


__all__ = [
    "CANCELLED",
    "CANCEL_REQUESTED",
    "COMPLETED",
    "FAILED",
    "InMemoryRunControlStore",
    "RedisRunControlStore",
    "RUNNING",
    "RunControlStore",
    "RunStatus",
]
