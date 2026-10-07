"""V2 Agent 提示词层。

提示词和 Agent 的状态校验分离。提示词负责指导模型，Agent 负责验证模型，
LangGraph 负责决定下一个节点。
"""

from .v2 import build_prompt

__all__ = ["build_prompt"]
