"""所有研究 Agent 共享的最小接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.state import ResearchState


class BaseAgent(ABC):
    """Agent 的基础约定。

    每个具体 Agent 只需要实现 ``run``：读取当前状态，完成自己的工作，
    再返回更新后的状态。这样工作流不需要知道每个 Agent 的内部细节。
    """

    name: str = "base"

    @abstractmethod
    async def run(self, state: ResearchState) -> ResearchState:
        """处理一次研究状态。"""
        raise NotImplementedError
