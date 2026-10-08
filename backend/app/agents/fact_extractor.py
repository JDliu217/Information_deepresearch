"""从候选来源中提取带来源的结构化事实。"""

from __future__ import annotations

import asyncio
from datetime import datetime
import hashlib
import re
import uuid
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from app.core.llm_client import LLMClient
from app.domain.models import DataPoint
from app.domain.state import ResearchState

from .base import BaseAgent


class FactExtractorAgent(BaseAgent):
    """把网页来源转换成报告可以引用的事实。"""

    name = "fact_extractor"
    SEARCH_ANALYSIS_SYSTEM = "你是专业的研究分析师，擅长从搜索结果中提取结构化信息、验证假设并评估来源质量。"
    SEARCH_ANALYSIS_PROMPT = r"""你是一位资深的研究分析师，擅长从搜索结果中提取关键信息，并验证研究假设。

## 研究问题
{query}

## 当前研究章节
标题: {section_title}
描述: {section_description}

## 研究假设（需要寻找证据支持或反驳）
{hypotheses}

## 搜索结果
{search_results}

## 任务
1. 分析搜索结果，提取结构化信息
2. 寻找支持或反驳研究假设的证据
3. 如果文章引用了数据来源（如"据XX统计"），生成追溯查询

输出JSON格式：
```json
{{
    "extracted_facts": [
        {{
            "content": "提取的事实陈述（要具体、可验证）",
            "source_name": "来源名称",
            "source_url": "来源URL",
            "source_type": "official/academic/news/report/self_media",
            "credibility_score": 0.0-1.0,
            "data_points": [
                {{"name": "指标名", "value": "数值", "unit": "单位", "year": 2024}}
            ],
            "needs_verification": true或false,
            "importance": "high/medium/low",
            "related_hypothesis": "h_1或h_2或null",
            "hypothesis_support": "supports/refutes/neutral"
        }}
    ],
    "hypothesis_evidence": [
        {{
            "hypothesis_id": "h_1",
            "evidence_type": "supports/refutes/inconclusive",
            "evidence_summary": "证据摘要"
        }}
    ],
    "entities_discovered": [
        {{"name": "实体名", "type": "company/person/policy/technology", "relations": ["与XX相关"]}}
    ],
    "key_insights": ["从这些结果中得到的关键洞察"],
    "follow_up_queries": ["需要进一步搜索的关键词"],
    "source_tracing_queries": ["追溯原始数据源的搜索词，如'国家统计局 2024 汽车销量'"],
    "missing_info": ["仍然缺失的信息"],
    "source_quality_assessment": "对整体来源质量的评估"
}}
```

## 评分标准
- 官方来源（政府、央企）: 0.9-1.0
- 学术来源（论文、研究机构）: 0.8-0.95
- 权威媒体（央媒、财经媒体）: 0.7-0.85
- 行业报告（券商、咨询）: 0.7-0.9
- 一般新闻: 0.5-0.7
- 自媒体: 0.2-0.5

请开始分析："""
    SUPPLEMENTARY_ANALYSIS_SYSTEM = "你是专业的信息提取专家，擅长从搜索结果中提取结构化信息。"
    SUPPLEMENTARY_ANALYSIS_PROMPT = r"""你是一位专业的研究分析师，正在补充搜索以解决审核发现的信息缺失问题。

## 原始研究问题
{original_query}

## 补充搜索关键词
{search_query}

## 搜索结果
{search_results}

## 任务
从搜索结果中提取与"{search_query}"直接相关的关键事实和数据。

输出JSON格式：
```json
{{
    "extracted_facts": [
        {{
            "content": "提取的事实陈述",
            "source_name": "来源名称",
            "source_url": "来源URL",
            "source_type": "official/academic/news/report",
            "credibility_score": 0.0-1.0,
            "data_points": [
                {{"name": "指标名", "value": "数值", "unit": "单位"}}
            ]
        }}
    ],
    "key_findings": "本次补充搜索的关键发现"
}}
```"""
    DEEP_SEARCH_ANALYSIS_SYSTEM = "你是专业的信息验证专家，擅长从搜索结果中提取权威信息并追溯原始来源。"
    DEEP_SEARCH_ANALYSIS_PROMPT = r"""你是一位专业的研究分析师，正在{search_type_desc}以获取更权威的信息。

## 原始研究问题
{original_query}

## 当前搜索关键词
{search_query}

{hypotheses_text}

## 搜索结果
{search_results}

## 任务
1. 从搜索结果中提取关键事实和数据（特别关注官方来源和权威数据）
2. 如果发现引用了其他权威来源，生成进一步追溯查询

输出JSON格式：
```json
{{
    "extracted_facts": [
        {{
            "content": "提取的事实陈述（要具体、可验证）",
            "source_name": "来源名称",
            "source_url": "来源URL",
            "source_type": "official/academic/news/report",
            "credibility_score": 0.0-1.0,
            "related_hypothesis": "h_1或null",
            "hypothesis_support": "supports/refutes/neutral"
        }}
    ],
    "data_points": [
        {{"name": "指标名", "value": "数值", "unit": "单位", "year": 2024}}
    ],
    "further_tracing_queries": ["如果发现引用了其他权威来源，建议进一步追溯的查询"],
    "source_reliability": "对本次搜索来源可靠性的评估"
}}
```"""
    DEEP_READ_PROMPT = r"""你是一位专业的文档分析师，擅长从长文本中提取关键信息。

## 研究问题
{query}

## 文档来源
URL: {url}
标题: {title}

## 文档内容
{content}

## 任务
深度阅读文档，提取与研究问题相关的所有关键信息。

输出JSON格式：
```json
{{
    "summary": "文档核心内容摘要（200字内）",
    "key_facts": [
        {{
            "content": "关键事实",
            "confidence": 0.0-1.0,
            "page_location": "大概位置描述"
        }}
    ],
    "data_tables": [
        {{
            "title": "数据表标题",
            "headers": ["列1", "列2"],
            "rows": [["值1", "值2"]]
        }}
    ],
    "quotes": ["重要原文引用"],
    "related_entities": ["提到的相关实体"],
    "publication_date": "发布日期（如果能识别）",
    "author_authority": "作者/机构权威性评估"
}}
```"""
    SUPPLEMENTARY_SEARCH_PROMPT = """请根据当前缺口生成少量可执行的补充搜索查询和来源追溯查询。查询应
具体到章节、时间、指标或权威机构，避免重复已有查询。"""
    # 原项目的常规搜索分析只发送每条摘要的前 300 字。
    default_max_source_chars = 300
    default_max_sources_per_section = 15
    default_max_total_source_chars = 4_500
    max_concurrent_sections = 3
    max_supplementary_sources_per_query = 8
    max_recursive_sources_per_query = 6

    def __init__(
        self,
        llm: LLMClient,
        *,
        max_source_chars: int = default_max_source_chars,
        max_total_source_chars: int = default_max_total_source_chars,
        max_sources_per_section: int = default_max_sources_per_section,
    ):
        if max_source_chars < 100:
            raise ValueError("max_source_chars 不能小于 100")
        if max_total_source_chars < max_source_chars:
            raise ValueError("max_total_source_chars 不能小于 max_source_chars")
        if max_sources_per_section < 1:
            raise ValueError("max_sources_per_section 必须大于 0")
        self.llm = llm
        self.max_source_chars = max_source_chars
        self.max_total_source_chars = max_total_source_chars
        self.max_sources_per_section = max_sources_per_section

    async def run(self, state: ResearchState, *, mode: str = "normal") -> ResearchState:
        """Analyze one search batch using the reference DeepScout mode.

        ``mode`` is ``normal`` for planned section research,
        ``supplementary`` for Critic initiated searches, or ``recursive`` for
        source-tracing/follow-up searches generated by DeepScout itself.
        """
        if mode not in {"normal", "supplementary", "recursive"}:
            raise ValueError("FactExtractor mode 必须是 normal、supplementary 或 recursive")
        if not state.raw_sources:
            raise ValueError("没有可供事实提取的来源")

        sections = self._sources_by_section(state.raw_sources, mode=mode)
        if not sections:
            state.phase = "researching"
            return state

        all_facts: list[dict[str, Any]] = []
        all_entities: list[dict[str, Any]] = []
        all_insights: list[str] = []
        follow_up_queries: list[str] = []
        follow_up_contexts: dict[str, list[dict[str, str]]] = {}
        hypothesis_evidence: list[dict[str, Any]] = []
        recursive_facts: list[dict[str, Any]] = []
        standalone_data_points: list[dict[str, Any]] = []
        analysis_notes: list[dict[str, Any]] = []
        section_inputs: list[dict[str, Any]] = []
        for section_id, section_sources in sections:
            section = next(
                (
                    item
                    for item in state.outline
                    if str(item.get("id", "")).strip() == section_id
                ),
                {},
            )
            section_title = section.get("title") or section_sources[0].get("section_title", "")
            if mode == "normal":
                analysis_groups = [
                    {
                        "mode": mode,
                        "search_type": "web",
                        "query": "",
                        "sources": section_sources[: self.max_sources_per_section],
                    }
                ]
            else:
                source_limit = (
                    self.max_supplementary_sources_per_query
                    if mode == "supplementary"
                    else self.max_recursive_sources_per_query
                )
                analysis_groups = self._group_sources_by_query(
                    section_sources,
                    mode=mode,
                    fallback_query=section_title or state.query,
                    source_limit=source_limit,
                )
            section_inputs.append(
                {
                    "section_id": section_id,
                    "section_sources": section_sources,
                    "section_title": section_title,
                    "section_description": section.get("description", ""),
                    "analysis_groups": analysis_groups,
                }
            )

        semaphore = asyncio.Semaphore(self.max_concurrent_sections)

        async def analyze_section(section_input: dict[str, Any]) -> Any:
            async with semaphore:
                # DeepScout performs supplementary and recursive analyses one
                # query at a time. Keep each section's query order stable.
                results = []
                for group in section_input["analysis_groups"]:
                    payload, system_prompt, user_prompt = self._build_analysis_request(
                        state,
                        group,
                        section_id=section_input["section_id"],
                        section_title=section_input["section_title"],
                        section_description=section_input["section_description"],
                    )
                    result = await self._complete_json(
                        payload,
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=0.2,
                        max_tokens=16000 if mode == "normal" else None,
                    )
                    results.append({"group": group, "result": result})
                return results

        # DeepScout runs up to three section jobs at once. Keep the same bound
        # here while parsing and merging results later in outline/source order.
        section_results = await asyncio.gather(
            *(analyze_section(section_input) for section_input in section_inputs)
        )

        for section_input, grouped_results in zip(section_inputs, section_results):
            section_id = section_input["section_id"]
            section_sources = section_input["section_sources"]
            for grouped_result in grouped_results:
                group = grouped_result["group"]
                result = grouped_result["result"]
                optional_warnings: list[str] = []
                if not isinstance(result, dict):
                    result = {}
                    optional_warnings.append("模型结果不是 JSON 对象，已忽略该查询分析结果")
                raw_facts = self._normalize_extracted_facts(result, optional_warnings)
                facts = self._validate_facts(
                    raw_facts,
                    group["sources"],
                    state.hypotheses,
                    optional_warnings,
                )
                if section_id:
                    for fact in facts:
                        fact["section_id"] = section_id
                        fact["section_title"] = str(section_input["section_title"])
                        fact["related_sections"] = [section_id]

                if group["mode"] == "supplementary":
                    # The reference supplementary pass persists facts only;
                    # its prompt's data_points/key_findings are not merged.
                    for fact in facts:
                        fact.pop("data_points", None)
                        fact.pop("section_id", None)
                        fact.pop("section_title", None)
                        fact["related_sections"] = []
                    all_facts.extend(facts)
                elif group["mode"] == "recursive":
                    all_facts.extend(facts)
                    recursive_facts.extend(facts)
                    standalone_data_points.extend(
                        self._validate_recursive_data_points(
                            result.get("data_points", []),
                            query=group["query"],
                            warnings=optional_warnings,
                        )
                    )
                    for query in self._optional_string_list(
                        result, "further_tracing_queries", optional_warnings
                    )[:2]:
                        follow_up_queries.append(query)
                        contexts = follow_up_contexts.setdefault(query, [])
                        context = {
                            "section_id": section_id or "",
                            "section_title": str(section_input["section_title"]),
                            "search_type": group["search_type"],
                        }
                        if context not in contexts:
                            contexts.append(context)
                    hypothesis_evidence.extend(
                        self._validate_hypothesis_evidence(
                            result.get("hypothesis_evidence", []),
                            state.hypotheses,
                            optional_warnings,
                        )
                    )
                else:
                    all_facts.extend(facts)
                    all_entities.extend(
                        self._validate_entities(
                            result.get("entities_discovered", []), optional_warnings
                        )
                    )
                    all_insights.extend(
                        self._optional_string_list(result, "key_insights", optional_warnings)
                    )
                    section_context = {
                        "section_id": section_id or "",
                        "section_title": str(section_input["section_title"]),
                    }
                    for field_name, search_type in (
                        ("source_tracing_queries", "source_tracing"),
                        ("follow_up_queries", "follow_up"),
                    ):
                        for query in self._optional_string_list(
                            result, field_name, optional_warnings
                        )[:2]:
                            follow_up_queries.append(query)
                            contexts = follow_up_contexts.setdefault(query, [])
                            context = {**section_context, "search_type": search_type}
                            if context not in contexts:
                                contexts.append(context)
                    hypothesis_evidence.extend(
                        self._validate_hypothesis_evidence(
                            result.get("hypothesis_evidence", []),
                            state.hypotheses,
                            optional_warnings,
                        )
                    )

                analysis_notes.append(
                    {
                        "agent": self.name,
                        "section_id": section_id,
                        "search_query": group["query"],
                        "analysis_mode": group["mode"],
                        "source_quality_assessment": str(
                            result.get(
                                "source_quality_assessment",
                                result.get("source_reliability", ""),
                            )
                        ),
                        "missing_info": self._optional_string_list(
                            result, "missing_info", optional_warnings
                        )
                        if group["mode"] == "normal"
                        else [],
                    }
                )
                if optional_warnings:
                    analysis_notes.append(
                        {
                            "agent": self.name,
                            "section_id": section_id,
                            "warning": "ignored_invalid_optional_fields",
                            "details": optional_warnings[:20],
                        }
                    )

        all_facts = self._deduplicate_facts(all_facts)
        state.facts = self._deduplicate_facts(state.facts + all_facts)
        self._append_data_points(state.data_points, all_facts)
        self._append_data_points(
            state.data_points,
            [{"data_points": standalone_data_points}],
        )
        self._apply_structured_hypothesis_evidence(state.hypotheses, hypothesis_evidence)
        self._apply_hypothesis_evidence(state.hypotheses, recursive_facts)
        self._update_knowledge_graph(state.knowledge_graph, all_entities)
        state.insights = list(dict.fromkeys([*state.insights, *all_insights]))
        pending_queries = list(dict.fromkeys([*state.pending_search_queries, *follow_up_queries]))
        pending_contexts = dict(state.pending_search_contexts)
        for query in pending_queries:
            contexts = pending_contexts.setdefault(query, [])
            for context in follow_up_contexts.get(query, []):
                if context not in contexts:
                    contexts.append(context)
        state.pending_search_queries = pending_queries
        state.pending_search_contexts = {
            query: pending_contexts[query]
            for query in pending_queries
            if query in pending_contexts
        }
        state.logs.extend(analysis_notes)
        for section_id, section_sources in sections:
            marker = section_id or "__unassigned__"
            for source in section_sources:
                extracted = source.setdefault("fact_extracted_sections", [])
                if marker not in extracted:
                    extracted.append(marker)
        state.phase = "researching"
        return state

    @classmethod
    def _format_search_analysis_prompt(
        cls,
        query: str,
        section_title: str,
        section_description: str,
        hypotheses: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> str:
        hypotheses_text = "无特定假设"
        if hypotheses:
            hypotheses_text = "\n".join(
                f"- [{item.get('id')}] {item.get('content')} "
                f"(状态: {item.get('status', 'unverified')})"
                for item in hypotheses
            )
        search_results = "".join(
            f"\n[{index}] {source.get('title') or 'N/A'}\n"
            f"URL: {source.get('url', '')}\n"
            f"来源: {source.get('source') or 'N/A'}\n"
            f"日期: {source.get('date') or 'N/A'}\n"
            f"摘要: {source.get('summary', '')[:300]}\n"
            for index, source in enumerate(sources, start=1)
        )
        return cls.SEARCH_ANALYSIS_PROMPT.format(
            query=query,
            section_title=section_title,
            section_description=section_description,
            hypotheses=hypotheses_text,
            search_results=search_results,
        )

    def _build_analysis_request(
        self,
        state: ResearchState,
        group: dict[str, Any],
        *,
        section_id: str | None,
        section_title: str,
        section_description: str,
    ) -> tuple[dict[str, Any], str, str]:
        source_context = self._build_source_context(group["sources"])
        mode = group["mode"]
        if mode == "normal":
            payload = {
                "mode": "search_analysis",
                "query": state.query,
                "section": {
                    "id": section_id,
                    "title": section_title,
                    "description": section_description,
                },
                "sources": source_context,
                "hypotheses": state.hypotheses,
            }
            user_prompt = self._format_search_analysis_prompt(
                state.query,
                section_title,
                section_description,
                state.hypotheses,
                source_context,
            )
            return payload, self.SEARCH_ANALYSIS_SYSTEM, user_prompt

        if mode == "supplementary":
            payload = {
                "mode": "supplementary_search",
                "query": state.query,
                "search_query": group["query"],
                "sources": source_context,
            }
            search_results = "\n".join(
                "标题: {title}\n来源: {source}\n内容: {summary}".format(
                    title=source.get("title") or "N/A",
                    source=source.get("source") or "N/A",
                    summary=str(source.get("summary", ""))[:300],
                )
                for source in source_context
            )
            user_prompt = self.SUPPLEMENTARY_ANALYSIS_PROMPT.format(
                original_query=state.query,
                search_query=group["query"],
                search_results=search_results,
            )
            return payload, self.SUPPLEMENTARY_ANALYSIS_SYSTEM, user_prompt

        if mode == "recursive":
            hypotheses = state.hypotheses[:3]
            hypotheses_text = ""
            if hypotheses:
                hypotheses_text = "## 研究假设\n" + "\n".join(
                    f"- [{hypothesis.get('id')}] {hypothesis.get('content')}"
                    for hypothesis in hypotheses
                )
            search_type_desc = (
                "追溯原始数据源"
                if group["search_type"] == "source_tracing"
                else "追踪相关线索"
            )
            payload = {
                "mode": "deep_search",
                "query": state.query,
                "search_query": group["query"],
                "search_type": group["search_type"],
                "sources": source_context,
                "hypotheses": hypotheses,
            }
            search_results = "\n".join(
                "标题: {title}\n来源: {source}\n内容: {summary}".format(
                    title=source.get("title") or "N/A",
                    source=source.get("source") or "N/A",
                    summary=str(source.get("summary", ""))[:300],
                )
                for source in source_context
            )
            user_prompt = self.DEEP_SEARCH_ANALYSIS_PROMPT.format(
                search_type_desc=search_type_desc,
                original_query=state.query,
                search_query=group["query"],
                hypotheses_text=hypotheses_text,
                search_results=search_results,
            )
            return payload, self.DEEP_SEARCH_ANALYSIS_SYSTEM, user_prompt

        raise ValueError(f"未知的事实分析模式：{mode}")

    @staticmethod
    def _sources_by_section(
        sources: list[dict[str, Any]],
        *,
        mode: str = "normal",
    ) -> list[tuple[str | None, list[dict[str, Any]]]]:
        grouped: dict[str | None, list[dict[str, Any]]] = {}
        for source in sources:
            source_mode = str(source.get("analysis_mode", "normal")).strip()
            if source_mode != mode:
                continue
            ids = source.get("section_ids") or [source.get("section_id")]
            for raw_id in ids:
                section_id = str(raw_id or "").strip() or None
                marker = section_id or "__unassigned__"
                if marker not in source.get("fact_extracted_sections", []):
                    grouped.setdefault(section_id, []).append(source)
        return list(grouped.items())

    @staticmethod
    def _group_sources_by_query(
        sources: list[dict[str, Any]],
        *,
        mode: str,
        fallback_query: str,
        source_limit: int,
    ) -> list[dict[str, Any]]:
        """Keep each supplementary/recursive search result batch separate."""

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for source in sources:
            search_type = str(source.get("search_type", "follow_up")).strip() or "follow_up"
            query = str(source.get("query", "")).strip() or fallback_query
            grouped.setdefault((search_type, query), []).append(source)
        return [
            {
                "mode": mode,
                "search_type": search_type,
                "query": query,
                "sources": grouped_sources[:source_limit],
            }
            for (search_type, query), grouped_sources in grouped.items()
        ]

    @staticmethod
    def _normalize_extracted_facts(
        result: dict[str, Any],
        warnings: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Map the reference DeepScout response to the local fact contract."""

        extracted = result.get("extracted_facts", [])
        if extracted is None:
            return []
        if not isinstance(extracted, list):
            if warnings is not None:
                warnings.append("extracted_facts 不是列表，已忽略本章节的事实结果")
            return []

        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(extracted, start=1):
            if not isinstance(item, dict):
                if warnings is not None:
                    warnings.append(f"第 {index} 个事实不是对象，已忽略")
                continue
            normalized.append(
                {
                    **item,
                    "source_title": item.get("source_title") or item.get("source_name", ""),
                    "confidence": item.get("confidence", item.get("credibility_score", 0.5)),
                }
            )
        return normalized

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            return []
        return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))

    @staticmethod
    def _optional_string_list(
        result: dict[str, Any],
        field: str,
        warnings: list[str],
    ) -> list[str]:
        value = result.get(field, [])
        if value is None:
            return []
        if not isinstance(value, list):
            warnings.append(f"{field} 不是列表，已忽略")
            return []
        items: list[str] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, str) or not item.strip():
                warnings.append(f"{field} 第 {index} 项不是有效字符串，已忽略")
                continue
            clean = item.strip()
            if clean not in items:
                items.append(clean)
        return items

    @staticmethod
    def _validate_hypothesis_evidence(
        value: Any,
        hypotheses: list[dict[str, Any]],
        warnings: list[str] | None = None,
    ) -> list[dict[str, str]]:
        if value is None:
            return []
        if not isinstance(value, list):
            if warnings is not None:
                warnings.append("hypothesis_evidence 不是列表")
            return []
        valid_ids = {str(item.get("id", "")).strip() for item in hypotheses}
        evidence: list[dict[str, str]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                if warnings is not None:
                    warnings.append(f"hypothesis_evidence 第 {index} 项不是对象")
                continue
            hypothesis_id = str(item.get("hypothesis_id", "")).strip()
            evidence_type = FactExtractorAgent._normalize_hypothesis_support(
                item.get("evidence_type")
            )
            summary = str(item.get("evidence_summary") or "").strip()
            if hypothesis_id not in valid_ids or not evidence_type or not summary:
                if warnings is not None:
                    warnings.append(f"hypothesis_evidence 第 {index} 项关联或摘要无效")
                continue
            evidence.append({
                "hypothesis_id": hypothesis_id,
                "evidence_type": "inconclusive" if evidence_type == "neutral" else evidence_type,
                "evidence_summary": summary,
            })
        return evidence

    @staticmethod
    def _validate_recursive_data_points(
        value: Any,
        *,
        query: str,
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Normalize DeepScout's top-level recursive-search data points."""

        if value is None:
            return []
        if not isinstance(value, list):
            warnings.append("data_points 不是列表，已忽略")
            return []

        points: list[dict[str, Any]] = []
        for index, raw_point in enumerate(value, start=1):
            if not isinstance(raw_point, dict):
                warnings.append(f"data_points 第 {index} 项不是对象，已忽略")
                continue
            name = raw_point.get("name")
            point_value = raw_point.get("value")
            if (
                not isinstance(name, str)
                or not name.strip()
                or point_value is None
                or (isinstance(point_value, str) and not point_value.strip())
            ):
                warnings.append(f"data_points 第 {index} 项缺少 name 或 value，已忽略")
                continue

            raw_year = raw_point.get("year")
            year = None
            if raw_year is not None:
                if isinstance(raw_year, bool):
                    warnings.append(f"data_points 第 {index} 项 year 无效，已使用 null")
                else:
                    try:
                        year = int(raw_year)
                    except (TypeError, ValueError):
                        warnings.append(f"data_points 第 {index} 项 year 无效，已使用 null")

            try:
                confidence = float(raw_point.get("confidence", 0.7))
            except (TypeError, ValueError):
                confidence = 0.7
                warnings.append(f"data_points 第 {index} 项 confidence 无效，已使用 0.7")
            confidence = min(max(confidence, 0.0), 1.0)
            points.append(
                {
                    "name": name.strip(),
                    "value": point_value,
                    "unit": str(raw_point.get("unit", "")).strip(),
                    "year": year,
                    "source": str(raw_point.get("source") or query).strip(),
                    "confidence": confidence,
                }
            )
        return points

    @staticmethod
    def _normalize_hypothesis_support(value: Any) -> str:
        """Only map unambiguous directions; uncertain votes are discarded."""

        if not isinstance(value, str):
            return ""
        return {
            "supports": "supports",
            "support": "supports",
            "支持": "supports",
            "refutes": "refutes",
            "refute": "refutes",
            "反驳": "refutes",
            "neutral": "neutral",
            "inconclusive": "neutral",
            "中立": "neutral",
            "无法判断": "neutral",
        }.get(value.strip().lower(), "")

    @staticmethod
    def _apply_structured_hypothesis_evidence(
        hypotheses: list[dict[str, Any]],
        evidence: list[dict[str, str]],
    ) -> None:
        by_id = {str(item.get("id", "")).strip(): item for item in hypotheses}
        for item in evidence:
            hypothesis = by_id.get(item["hypothesis_id"])
            if hypothesis is None:
                continue
            evidence_type = item["evidence_type"]
            if evidence_type == "supports":
                evidence_for = hypothesis.setdefault("evidence_for", [])
                evidence_for.append(item["evidence_summary"])
                if len(evidence_for) >= 2:
                    hypothesis["status"] = "supported"
            elif evidence_type == "refutes":
                evidence_against = hypothesis.setdefault("evidence_against", [])
                evidence_against.append(item["evidence_summary"])
                if len(evidence_against) >= 2:
                    hypothesis["status"] = "refuted"
            elif hypothesis.get("status", "unverified") == "unverified":
                hypothesis["status"] = "partially_supported"

    def _build_source_context(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """压缩网页正文，避免事实提取请求超过模型上下文或输出预算。"""

        context: list[dict[str, Any]] = []
        total_chars = 0
        for source in sources:
            original = str(
                source.get("summary") or source.get("snippet") or source.get("content") or ""
            ).strip()
            remaining = self.max_total_source_chars - total_chars
            summary = original[: min(self.max_source_chars, max(remaining, 0))]
            total_chars += len(summary)
            item = {
                "title": str(source.get("title", "")).strip(),
                "url": str(source.get("url", "")).strip(),
                "source": str(source.get("source", "")).strip(),
                "date": str(source.get("date", "")).strip(),
                "query": str(source.get("query", "")).strip(),
                "summary": summary,
                "content": summary,
            }
            context.append(item)
        return context

    @staticmethod
    def _validate_entities(
        value: Any,
        warnings: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """保留格式正确的可选实体，忽略坏项而不阻断核心事实提取。"""

        def warn(message: str) -> None:
            if warnings is not None and len(warnings) < 50:
                warnings.append(message)

        if value is None:
            return []
        if not isinstance(value, list):
            warn("entities_discovered 不是列表")
            return []

        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                warn(f"第 {index} 个实体不是对象")
                continue

            raw_name = item.get("name")
            if not isinstance(raw_name, str) or not raw_name.strip():
                warn(f"第 {index} 个实体缺少 name")
                continue
            name = raw_name.strip()

            raw_relations = item.get("relations", [])
            if raw_relations is None:
                raw_relations = []
            if not isinstance(raw_relations, list):
                warn(f"第 {index} 个实体 relations 不是列表，已忽略关系")
                raw_relations = []

            relations: list[str] = []
            for relation_index, relation in enumerate(raw_relations, start=1):
                if not isinstance(relation, str):
                    warn(
                        f"第 {index} 个实体第 {relation_index} 个关系不是字符串"
                    )
                    continue
                relation = relation.strip()
                if relation:
                    relations.append(relation)

            raw_entity_type = item.get("type")
            if raw_entity_type is None:
                entity_type = "unknown"
            elif isinstance(raw_entity_type, str) and raw_entity_type.strip():
                entity_type = raw_entity_type.strip()
            else:
                warn(f"第 {index} 个实体 type 无效，已使用 unknown")
                entity_type = "unknown"
            validated.append(
                {
                    "name": name,
                    "type": entity_type,
                    "relations": relations,
                }
            )
        return validated

    @staticmethod
    def _update_knowledge_graph(
        graph: dict[str, Any],
        entities: list[dict[str, Any]],
    ) -> None:
        """把实体和关系累积到共享知识图谱，并对节点和边去重。"""
        if not isinstance(graph, dict):
            raise ValueError("knowledge_graph 必须是对象")

        nodes = graph.setdefault("nodes", [])
        edges = graph.setdefault("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("knowledge_graph 的 nodes 和 edges 必须是列表")

        existing_nodes = {
            str(node.get("name", "")).strip()
            for node in nodes
            if isinstance(node, dict)
        }

        for entity in entities:
            name = entity["name"]
            if not name or name in existing_nodes:
                continue

            nodes.append(
                {
                    "id": f"node_{len(nodes)}",
                    "name": name,
                    "type": entity["type"],
                    "discovered_at": datetime.now().isoformat(),
                }
            )
            existing_nodes.add(name)

            for relation in entity["relations"]:
                edges.append(
                    {
                        "source": name,
                        "relation": relation,
                        "discovered_at": datetime.now().isoformat(),
                    }
                )

    @staticmethod
    def _validate_facts(
        value: Any,
        sources: list[dict[str, Any]],
        hypotheses: list[dict[str, Any]],
        warnings: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            if warnings is not None:
                warnings.append("extracted_facts 不是列表，已忽略")
            return []

        source_by_url = {
            str(source.get("url", "")).strip(): source
            for source in sources
            if source.get("url")
        }
        # Keep the whitelist boundary, but tolerate URL formatting changes a
        # model commonly makes (whitespace, host case, and a trailing slash).
        # The stored URL remains the exact URL returned by the search client.
        canonical_urls = {
            FactExtractorAgent._canonical_url(url): url
            for url in source_by_url
            if FactExtractorAgent._canonical_url(url)
        }
        hypothesis_ids = {
            str(hypothesis.get("id", "")).strip()
            for hypothesis in hypotheses
            if hypothesis.get("id")
        }
        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                if warnings is not None:
                    warnings.append(f"第 {index} 个事实不是对象，已忽略")
                continue

            content = str(item.get("content") or "").strip()
            source_url = str(item.get("source_url") or "").strip()
            if not content or not source_url:
                if warnings is not None:
                    warnings.append(
                        f"第 {index} 个事实缺少 content 或 source_url，已忽略该事实"
                    )
                continue
            matched_url = source_url
            if matched_url not in source_by_url:
                matched_url = canonical_urls.get(
                    FactExtractorAgent._canonical_url(source_url), ""
                )
            if not matched_url:
                if warnings is not None:
                    warnings.append(f"第 {index} 个事实引用了未提供的来源 URL，已忽略该事实")
                continue
            source_url = matched_url

            try:
                confidence = float(
                    item.get("confidence", item.get("credibility_score", 0.5))
                )
            except (TypeError, ValueError):
                confidence = 0.5
                if warnings is not None:
                    warnings.append(f"第 {index} 个事实 confidence 无效，已使用 0.5")
            confidence = min(max(confidence, 0.0), 1.0)

            source_context = source_by_url[source_url]
            source_name = str(
                item.get("source_name")
                or item.get("source_title")
                or source_context.get("source")
                or ""
            ).strip()
            fact = {
                "id": str(item.get("id", "")).strip() or f"fact_{uuid.uuid4().hex[:8]}",
                "content": content,
                "source_name": source_name,
                "source_title": source_name,
                "source_url": source_url,
                "source_type": str(item.get("source_type", "news")).strip() or "news",
                "credibility_score": confidence,
                "confidence": confidence,
                "extracted_at": datetime.now().isoformat(),
                "related_sections": [],
                "verified": False,
                "metadata": {},
            }
            raw_data_points = item.get("data_points", [])
            if raw_data_points is None:
                raw_data_points = []
            if not isinstance(raw_data_points, list):
                if warnings is not None:
                    warnings.append(f"第 {index} 个事实 data_points 不是列表，已忽略")
                raw_data_points = []

            normalized_data_points: list[dict[str, Any]] = []
            for point_index, raw_point in enumerate(raw_data_points, start=1):
                if not isinstance(raw_point, dict):
                    if warnings is not None:
                        warnings.append(
                            f"第 {index} 个事实第 {point_index} 个数据点不是对象，已忽略"
                        )
                    continue
                name = str(raw_point.get("name", "")).strip()
                value = raw_point.get("value")
                if not name or value is None or (isinstance(value, str) and not value.strip()):
                    if warnings is not None:
                        warnings.append(
                            f"第 {index} 个事实第 {point_index} 个数据点缺少 name 或 value，已忽略"
                        )
                    continue

                raw_year = raw_point.get("year")
                year = None
                if raw_year is not None:
                    if isinstance(raw_year, bool):
                        if warnings is not None:
                            warnings.append(
                                f"第 {index} 个事实第 {point_index} 个数据点 year 无效，已使用 null"
                            )
                        raw_year = None
                    try:
                        if raw_year is not None:
                            year = int(raw_year)
                    except (TypeError, ValueError):
                        if warnings is not None:
                            warnings.append(
                                f"第 {index} 个事实第 {point_index} 个数据点 year 无效，已使用 null"
                            )
                        year = None

                try:
                    point_confidence = float(raw_point.get("confidence", confidence))
                except (TypeError, ValueError):
                    point_confidence = confidence
                    if warnings is not None:
                        warnings.append(
                            f"第 {index} 个事实第 {point_index} 个数据点 confidence 无效，已使用事实可信度"
                        )
                point_confidence = min(max(point_confidence, 0.0), 1.0)

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
            hypothesis_support = FactExtractorAgent._normalize_hypothesis_support(
                item.get("hypothesis_support")
            )
            if related_hypothesis in hypothesis_ids and hypothesis_support:
                fact["related_hypothesis"] = related_hypothesis
                fact["hypothesis_support"] = hypothesis_support
            elif related_hypothesis or item.get("hypothesis_support"):
                if warnings is not None:
                    warnings.append(f"第 {index} 个事实的假设关联无效")

            for field_name in ("section_id", "section_title"):
                if source_context.get(field_name):
                    fact[field_name] = source_context[field_name]
            validated.append(fact)
        return validated

    @staticmethod
    def _canonical_url(value: Any) -> str:
        """Return a comparison-only URL form without broadening the source whitelist."""

        if not isinstance(value, str):
            return ""
        value = value.strip()
        if not value:
            return ""
        try:
            parsed = urlsplit(value)
        except ValueError:
            return value
        if not parsed.scheme or not parsed.netloc:
            return value
        path = parsed.path.rstrip("/") or "/"
        return urlunsplit(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                path,
                parsed.query,
                "",  # fragments do not identify a different search source
            )
        )

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

    @staticmethod
    def _deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        fingerprints: dict[str, str] = {}
        retained: list[dict[str, Any]] = []
        for fact in facts:
            content = str(fact.get("content", "")).strip()
            source_url = str(fact.get("source_url", "")).strip()
            if not content:
                continue
            numbers = re.findall(r"\d+\.?\d*", content)
            keywords = re.findall(r"[\u4e00-\u9fa5]{2,4}", content)[:5]
            fingerprint = hashlib.md5(
                f"{','.join(numbers[:3])}|{','.join(keywords)}".encode()
            ).hexdigest()[:16]
            if fingerprint in fingerprints and fingerprints[fingerprint] != source_url:
                continue
            fingerprints.setdefault(fingerprint, source_url)
            retained.append(fact)
        return retained
