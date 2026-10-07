"""领域状态和对外事件的 JSON 序列化辅助函数。"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.domain.events import ResearchEvent
from app.domain.state import ResearchState


def state_to_dict(state: ResearchState) -> dict[str, Any]:
    """把 ResearchState 转换成可写入 JSON/JSONB 的普通字典。"""

    return asdict(state)


def event_to_record(event: dict[str, Any]) -> dict[str, Any]:
    """拆分 ResearchEvent 的公共字段和业务数据。"""

    required = {"type", "session_id", "phase", "iteration"}
    missing = required - event.keys()
    if missing:
        raise ValueError(f"研究事件缺少公共字段: {', '.join(sorted(missing))}")
    data = {key: value for key, value in event.items() if key not in required}
    ResearchEvent(
        type=event["type"],
        session_id=event["session_id"],
        phase=event["phase"],
        iteration=event["iteration"],
        data=data,
    )
    return {
        "session_id": event["session_id"],
        "sequence": int(event.get("sequence", 0)),
        "event_type": event["type"],
        "phase": event["phase"],
        "iteration": event["iteration"],
        "data": data,
    }
