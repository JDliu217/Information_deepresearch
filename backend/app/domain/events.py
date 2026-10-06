"""研究工作流对外发布的事件格式。

这一层先不绑定 SSE、WebSocket 或具体前端，只定义一个稳定的 Python
字典格式。以后无论接哪种传输方式，都可以把同一类事件发送给调用方。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


class ResearchEventType:
    """工作流允许对外发布的事件类型。"""

    RESEARCH_STARTED = "research_started"
    PHASE_STARTED = "phase_started"
    OUTLINE_READY = "outline_ready"
    RESEARCH_EVIDENCE_READY = "research_evidence_ready"
    DRAFT_READY = "draft_ready"
    REVIEW_COMPLETED = "review_completed"
    RESEARCH_COMPLETED = "research_completed"


EVENT_TYPES = frozenset(
    {
        ResearchEventType.RESEARCH_STARTED,
        ResearchEventType.PHASE_STARTED,
        ResearchEventType.OUTLINE_READY,
        ResearchEventType.RESEARCH_EVIDENCE_READY,
        ResearchEventType.DRAFT_READY,
        ResearchEventType.REVIEW_COMPLETED,
        ResearchEventType.RESEARCH_COMPLETED,
    }
)

RESEARCH_PHASES = frozenset(
    {
        "init",
        "planning",
        "researching",
        "analyzing",
        "writing",
        "reviewing",
        "re_researching",
        "revising",
        "completed",
    }
)

EVENT_REQUIRED_FIELDS = {
    ResearchEventType.RESEARCH_STARTED: frozenset({"query", "max_iterations"}),
    ResearchEventType.PHASE_STARTED: frozenset({"agent"}),
    ResearchEventType.OUTLINE_READY: frozenset(
        {"outline", "research_questions", "hypotheses", "key_entities", "mind_map"}
    ),
    ResearchEventType.RESEARCH_EVIDENCE_READY: frozenset(
        {"supplementary", "source_count", "fact_count", "sources", "facts", "references"}
    ),
    ResearchEventType.DRAFT_READY: frozenset(
        {"report", "outline", "draft_sections", "revision"}
    ),
    ResearchEventType.REVIEW_COMPLETED: frozenset(
        {"review_result", "critic_feedback", "quality_score"}
    ),
    ResearchEventType.RESEARCH_COMPLETED: frozenset(
        {"report", "quality_score", "references", "review_result", "critic_feedback"}
    ),
}

EVENT_ENVELOPE_FIELDS = frozenset({"type", "session_id", "phase", "iteration"})


@dataclass(frozen=True)
class ResearchEvent:
    """一次研究流程进度更新。

    ``data`` 中的字段会在 ``to_dict`` 时展开到事件顶层，调用方因此可以
    直接读取 ``event["report"]``、``event["references"]`` 等结果字段。
    """

    type: str
    session_id: str
    phase: str
    iteration: int = 0
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """校验所有事件共有的外层字段。"""
        if not isinstance(self.type, str) or self.type not in EVENT_TYPES:
            raise ValueError(f"不支持的研究事件类型: {self.type!r}")
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("研究事件 session_id 不能为空")
        if not isinstance(self.phase, str) or self.phase not in RESEARCH_PHASES:
            raise ValueError(f"不支持的研究阶段: {self.phase!r}")
        if isinstance(self.iteration, bool) or not isinstance(self.iteration, int):
            raise ValueError("研究事件 iteration 必须是整数")
        if self.iteration < 0:
            raise ValueError("研究事件 iteration 不能小于 0")
        if not isinstance(self.data, dict):
            raise ValueError("研究事件 data 必须是字典")
        reserved_fields = EVENT_ENVELOPE_FIELDS & self.data.keys()
        if reserved_fields:
            reserved = ", ".join(sorted(reserved_fields))
            raise ValueError(f"研究事件 data 不能覆盖公共字段: {reserved}")
        missing_fields = EVENT_REQUIRED_FIELDS[self.type] - self.data.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"{self.type} 缺少必需字段: {missing}")

    def to_dict(self) -> dict[str, Any]:
        """转换成可被 API、SSE 或测试直接使用的普通字典。"""
        event = {
            "type": self.type,
            "session_id": self.session_id,
            "phase": self.phase,
            "iteration": self.iteration,
        }
        event.update(deepcopy(self.data))
        return event

