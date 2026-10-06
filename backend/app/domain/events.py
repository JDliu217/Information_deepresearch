"""研究工作流对外发布的事件格式。

这一层先不绑定 SSE、WebSocket 或具体前端，只定义一个稳定的 Python
字典格式。以后无论接哪种传输方式，都可以把同一类事件发送给调用方。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


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

