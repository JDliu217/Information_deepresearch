"""统一的大模型客户端接口。

Agent 只依赖这里定义的接口，不直接依赖某一家模型服务的 SDK。
当前先实现 MockLLMClient，后续再实现真实的 OpenAI 兼容客户端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """所有 LLM 客户端都必须提供的能力。"""

    @abstractmethod
    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """让模型返回结构化 JSON 数据。"""
        raise NotImplementedError

    @abstractmethod
    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        """让模型返回普通文本。"""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """不联网的确定性客户端。

    Mock 的作用是先验证业务流程和状态流转，而不是模拟真正的智能程度。
    同样的输入会得到同样的输出，测试因此稳定且容易理解。
    """

    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if role != "planner":
            raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")

        query = str(payload.get("query", "")).strip()
        if not query:
            raise ValueError("planner 请求缺少 query")

        return {
            "plan": [
                {
                    "title": "现状与定义",
                    "description": f"明确“{query}”的研究范围和当前现状。",
                },
                {
                    "title": "问题与证据",
                    "description": "整理公开来源中的事实、数据和主要争议。",
                },
                {
                    "title": "趋势与建议",
                    "description": "根据已有证据判断未来趋势并提出建议。",
                },
            ],
            "research_questions": [
                f"{query} 的当前现状和关键定义是什么？",
                f"{query} 面临哪些主要问题，有哪些公开证据？",
                f"{query} 的未来趋势和改进建议是什么？",
            ],
        }

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        if role != "writer":
            raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")

        query = str(payload.get("query", "")).strip()
        return f"关于“{query}”的研究报告草稿。"
