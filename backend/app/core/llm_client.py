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
        if role == "planner":
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

        if role == "fact_extractor":
            facts = []
            for source in payload.get("sources", []):
                content = str(source.get("content") or source.get("snippet") or "").strip()
                url = str(source.get("url", "")).strip()
                if not content or not url:
                    continue
                facts.append(
                    {
                        "content": content,
                        "source_title": str(source.get("title", "")).strip(),
                        "source_url": url,
                        "source_type": "web",
                        "confidence": 0.7,
                    }
                )
            return {"facts": facts}

        if role == "critic":
            report = str(payload.get("report", "")).strip()
            facts = payload.get("facts", [])
            sources = payload.get("sources", [])
            if not report:
                raise ValueError("critic 请求缺少 report")

            passed = bool(facts and sources and "http" in report)
            return {
                "verdict": "pass" if passed else "needs_revision",
                "quality_score": 8.0 if passed else 4.0,
                "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
                "needs_more_research": not passed,
                "issues": [] if passed else ["需要补充带来源的事实"],
                "search_queries": [] if passed else ["补充权威来源和数据"],
            }

        raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        if role != "writer":
            raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")

        query = str(payload.get("query", "")).strip()
        if not query:
            raise ValueError("writer 请求缺少 query")

        facts = payload.get("facts", [])
        lines = [
            "## 执行摘要",
            "",
            f"本报告围绕“{query}”整理公开资料，并只使用已收集的来源作为证据。",
            "",
            "## 研究发现",
            "",
        ]
        if facts:
            for index, fact in enumerate(facts, start=1):
                content = str(fact.get("content", "")).strip()
                title = str(fact.get("source_title", "来源")).strip() or "来源"
                url = str(fact.get("source_url", "")).strip()
                lines.append(f"{index}. {content} ([{title}]({url}))")
        else:
            lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")

        review = payload.get("review", {})
        issues = review.get("issues", []) if isinstance(review, dict) else []
        if issues:
            lines.extend(["", "## 根据审核意见修订", ""])
            lines.extend(f"- 已处理：{issue}" for issue in issues)

        lines.extend(
            [
                "",
                "## 结论",
                "",
                "以上结论需要结合更多官方统计和行业报告继续验证。",
            ]
        )
        return "\n".join(lines)
