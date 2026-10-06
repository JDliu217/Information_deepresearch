"""从候选来源中提取带来源的结构化事实。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import DataPoint
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
                "hypotheses": state.hypotheses,
                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实；如果事实与某个研究假设相关，请标记关联假设和支持方向。",
            },
        )
        facts = self._validate_facts(
            result.get("facts"),
            state.raw_sources,
            state.hypotheses,
        )
        state.facts = self._deduplicate_facts(state.facts + facts)
        self._append_data_points(state.data_points, facts)
        self._apply_hypothesis_evidence(state.hypotheses, facts)
        state.phase = "researching"
        return state

    @staticmethod
    def _validate_facts(
        value: Any,
        sources: list[dict[str, Any]],
        hypotheses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ValueError("FactExtractor 返回的 facts 必须是列表")

        allowed_urls = {
            str(source.get("url", "")).strip()
            for source in sources
            if source.get("url")
        }
        source_by_url = {
            str(source.get("url", "")).strip(): source
            for source in sources
            if source.get("url")
        }
        hypothesis_ids = {
            str(hypothesis.get("id", "")).strip()
            for hypothesis in hypotheses
            if hypothesis.get("id")
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

            fact = {
                "content": content,
                "source_title": str(item.get("source_title", "")).strip(),
                "source_url": source_url,
                "source_type": str(item.get("source_type", "web")).strip() or "web",
                "confidence": confidence,
            }
            raw_data_points = item.get("data_points", [])
            if raw_data_points is None:
                raw_data_points = []
            if not isinstance(raw_data_points, list):
                raise ValueError(f"FactExtractor 的第 {index} 个事实 data_points 必须是列表")

            normalized_data_points: list[dict[str, Any]] = []
            for point_index, raw_point in enumerate(raw_data_points, start=1):
                if not isinstance(raw_point, dict):
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实第 {point_index} 个数据点不是对象"
                    )
                name = str(raw_point.get("name", "")).strip()
                value = raw_point.get("value")
                if not name or value is None or (isinstance(value, str) and not value.strip()):
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实第 {point_index} 个数据点缺少 name 或 value"
                    )

                raw_year = raw_point.get("year")
                year = None
                if raw_year is not None:
                    if isinstance(raw_year, bool):
                        raise ValueError(
                            f"FactExtractor 的第 {index} 个事实第 {point_index} 个数据点 year 无效"
                        )
                    try:
                        year = int(raw_year)
                    except (TypeError, ValueError) as exc:
                        raise ValueError(
                            f"FactExtractor 的第 {index} 个事实第 {point_index} 个数据点 year 无效"
                        ) from exc

                try:
                    point_confidence = float(raw_point.get("confidence", confidence))
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实第 {point_index} 个数据点 confidence 无效"
                    ) from exc
                if not 0 <= point_confidence <= 1:
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实第 {point_index} 个数据点 confidence 必须在 0 到 1 之间"
                    )

                normalized_data_points.append(
                    {
                        "name": name,
                        "value": value,
                        "unit": str(raw_point.get("unit", "")).strip(),
                        "year": year,
                        "source": str(
                            raw_point.get("source")
                            or item.get("source_title")
                            or source_url
                        ).strip(),
                        "confidence": point_confidence,
                    }
                )
            fact["data_points"] = normalized_data_points

            related_hypothesis = str(item.get("related_hypothesis") or "").strip()
            hypothesis_support = str(item.get("hypothesis_support") or "").strip()
            if related_hypothesis or hypothesis_support:
                if not related_hypothesis or not hypothesis_support:
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实假设关联字段必须同时提供"
                    )
                if related_hypothesis not in hypothesis_ids:
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实引用了未知假设"
                    )
                if hypothesis_support not in {"supports", "refutes", "neutral"}:
                    raise ValueError(
                        f"FactExtractor 的第 {index} 个事实 hypothesis_support 无效"
                    )
                fact["related_hypothesis"] = related_hypothesis
                fact["hypothesis_support"] = hypothesis_support

            source_context = source_by_url[source_url]
            for field_name in ("section_id", "section_title"):
                if source_context.get(field_name):
                    fact[field_name] = source_context[field_name]
            validated.append(fact)
        return validated

    @staticmethod
    def _append_data_points(
        target: list[dict[str, Any]],
        facts: list[dict[str, Any]],
    ) -> None:
        """把事实中的数据点写入共享状态，并按内容去重。"""
        seen = {
            (
                str(point.get("name", "")).strip(),
                str(point.get("value", "")).strip(),
                str(point.get("unit", "")).strip(),
                str(point.get("year", "")).strip(),
                str(point.get("source", "")).strip(),
            )
            for point in target
        }
        for fact in facts:
            for point in fact.get("data_points", []):
                key = (
                    point["name"],
                    str(point["value"]).strip(),
                    point["unit"],
                    str(point["year"] or "").strip(),
                    point["source"],
                )
                if key in seen:
                    continue
                target.append(
                    DataPoint(
                        id=f"dp_{len(target) + 1}",
                        name=point["name"],
                        value=point["value"],
                        unit=point["unit"],
                        year=point["year"],
                        source=point["source"],
                        confidence=point["confidence"],
                    ).to_dict()
                )
                seen.add(key)

    @staticmethod
    def _apply_hypothesis_evidence(
        hypotheses: list[dict[str, Any]],
        facts: list[dict[str, Any]],
    ) -> None:
        """将事实中的支持方向累积到对应假设。"""
        hypotheses_by_id = {
            str(hypothesis.get("id", "")).strip(): hypothesis
            for hypothesis in hypotheses
            if hypothesis.get("id")
        }
        for fact in facts:
            hypothesis_id = fact.get("related_hypothesis")
            if not hypothesis_id or hypothesis_id not in hypotheses_by_id:
                continue

            hypothesis = hypotheses_by_id[hypothesis_id]
            support = fact["hypothesis_support"]
            summary = str(fact.get("content", "")).strip()[:100]
            if support == "supports":
                evidence = hypothesis.setdefault("evidence_for", [])
                if summary not in evidence:
                    evidence.append(summary)
                if len(evidence) >= 2:
                    hypothesis["status"] = "supported"
            elif support == "refutes":
                evidence = hypothesis.setdefault("evidence_against", [])
                if summary not in evidence:
                    evidence.append(summary)
                if len(evidence) >= 2:
                    hypothesis["status"] = "refuted"
            elif hypothesis.get("status") == "unverified":
                hypothesis["status"] = "partially_supported"

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
