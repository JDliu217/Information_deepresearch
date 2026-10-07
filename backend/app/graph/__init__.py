"""LangGraph 编排层。

这里仅负责把已有领域状态和 Agent 连接成图。Agent 本身仍然位于
``app.agents``，对外事件仍然使用 ``app.domain.events`` 的协议。
"""

from .state import ResearchGraphState, initial_graph_state

__all__ = ["ResearchGraphState", "initial_graph_state"]
