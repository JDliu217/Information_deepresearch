"""从候选来源中提取带来源的结构化事实。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class FactExtractorAgent(BaseAgent):
    """把网页来源转换成报告可以引用的事实。"""

    name = "fact_extractor"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.raw_sources:
            raise ValueError("没有可供事实提取的来源")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "sources": state.raw_sources,
                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
            },
        )
        facts = self._validate_facts(result.get("facts"), state.raw_sources)
        state.facts = self._deduplicate_facts(state.facts + facts)
        state.phase = "researching"
        return state

    @staticmethod
    def _validate_facts(value: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ValueError("FactExtractor 返回的 facts 必须是列表")

        allowed_urls = {
            str(source.get("url", "")).strip()
            for source in sources
            if source.get("url")
        }
        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"FactExtractor 的第 {index} 个事实不是对象")

            content = str(item.get("content", "")).strip()
            source_url = str(item.get("source_url", "")).strip()
            if not content or not source_url:
                raise ValueError(f"FactExtractor 的第 {index} 个事实缺少 content 或 source_url")
            if source_url not in allowed_urls:
                raise ValueError(f"FactExtractor 的第 {index} 个事实引用了未知来源")

            try:
                confidence = float(item.get("confidence", 0.0))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 无效") from exc
            if not 0 <= confidence <= 1:
                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 必须在 0 到 1 之间")

            validated.append(
                {
                    "content": content,
                    "source_title": str(item.get("source_title", "")).strip(),
                    "source_url": source_url,
                    "source_type": str(item.get("source_type", "web")).strip() or "web",
                    "confidence": confidence,
                }
            )
        return validated

    @staticmethod
    def _deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[tuple[str, str], dict[str, Any]] = {}
        for fact in facts:
            key = (
                str(fact.get("source_url", "")).strip(),
                str(fact.get("content", "")).strip(),
            )
            if key != ("", ""):
                unique.setdefault(key, fact)
        return list(unique.values())
