"""Research planning agent.

The planner asks the model for a topic-specific JSON plan and validates its
declared subject before passing the outline to the search stage. Reference-style
flat responses are accepted only when they provide enough topic context.
"""

from __future__ import annotations

import json
import math
import re
import time
from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Hypothesis, Section
from app.domain.state import ResearchState

from .base import BaseAgent


class PlanningFailure(ValueError):
    """A planning error that carries the state and safe per-attempt trace."""

    def __init__(self, message: str, state: ResearchState) -> None:
        self.research_state = state
        self.diagnostics = state.planner_diagnostics
        super().__init__(message)


class PlannerAgent(BaseAgent):
    """Turn a research question into a searchable outline and hypotheses."""

    name = "planner"

    PLANNING_SYSTEM = (
        "你是一位专业的研究规划师，不预设研究领域。先识别用户问题中的研究对象和目标，"
        "再按该主题设计研究计划。严格按 JSON 格式输出，不要添加额外内容。"
    )
    REVISION_SYSTEM = "你是总架构师，需要判断是否需要调整研究计划。"
    PLANNING_PROMPT = r"""## 用户的研究问题
{query}

请先识别问题的核心研究对象和研究目标，再为这个问题设计研究计划。不能把问题改成另一个主题，也不能套用固定领域的大纲。

## 规划要求
1. 生成3-8个相互衔接的章节，章节结构要由当前研究对象和问题决定。人物研究可按生平阶段、时代背景、作品或影响组织；只有在用户问题确实涉及这些方面时才采用。
2. research_subject填写用户问题中的核心对象名称，优先沿用用户原文，不要另选对象；只写对象名称，不要把行业、时间范围和研究维度拼成更长的对象描述。公司与行业同时出现时，research_subject填写公司名，行业背景放入章节和 key_entities。每个章节都要明确回答研究问题的一部分，搜索词要体现该章节要查的具体方面。章节可以按主题使用对象的常见简称、所属行业或上下文表达，不要为了重复关键词让搜索词变得不自然。
3. 不要仅因为某类内容常见就加入无关的行业、组织、技术或政策分析。
4. 只有研究问题需要可量化证据时才设置 requires_data=true；只有存在可比较的数据且图表有帮助时才设置 requires_chart=true。定性研究应将二者设为 false。
5. 提出3-5个能由研究材料回答的具体问题。只有适合验证假设的课题才填写 hypotheses；描述性课题可以返回空列表，不要强造市场或趋势假设。
6. 不要在规划阶段编造事实、数据或来源。

## 输出格式
只返回一个 JSON 对象，格式如下：
{{
  "research_subject": "问题中的核心研究对象（参考工程扁平格式可省略）",
  "outline": [
    {{
      "id": "sec_1",
      "title": "与研究对象相关的章节标题",
      "description": "本章节需要回答的问题和覆盖范围",
      "section_type": "qualitative、quantitative 或 mixed",
      "requires_data": false,
      "requires_chart": false,
      "search_queries": ["围绕研究对象和章节内容的具体搜索词"]
    }}
  ],
  "research_questions": ["具体研究问题"],
  "hypotheses": [],
  "key_entities": [],
  "mind_map": {{}}
}}

outline必须有3-8章。所有章节、研究问题、假设和搜索词都必须与用户的研究问题直接相关。不要输出示例主题或模板占位文字。"""
    PLANNING_RETRY_PROMPT = r"""请修正上一轮没有通过校验的研究计划。

## 用户的研究问题
{query}

## 上一轮校验未通过的原因
{validation_error}

请只针对上述问题修正，不要更换研究对象或套用固定领域大纲。research_subject只写原问题中的核心对象名称，不要将行业、时间范围和研究维度拼入对象名称。保留3-8个实质相关章节；各章节描述和搜索词要共同覆盖用户指定的范围。参考工程的扁平字段格式 sec_n_title/sec_n_desc/sec_n_query 和标准 outline 格式都可接受；扁平格式没有 research_subject 时，系统会从用户问题推断。

严格返回完整 JSON 对象。不要解释、不要在 JSON 外添加文字；字段和类型应符合首次规划格式。标准格式结构如下：
{{"research_subject":"核心对象","outline":[{{"id":"sec_1","title":"章节标题","description":"章节范围","section_type":"mixed","requires_data":false,"requires_chart":false,"search_queries":["搜索词"]}}],"research_questions":[],"hypotheses":[],"key_entities":[],"mind_map":{{}}}}
outline必须包含3-8个章节，不能包含与用户问题无关的主题。"""
    REVISION_PROMPT = r"""你是总架构师，需要根据研究进展动态调整大纲。

## 原始问题
{query}

## 当前大纲
{current_outline}

## 新发现的重要信息
{new_findings}

## 当前进度
- 已完成章节: {completed_sections}
- 收集的事实数量: {facts_count}
- 发现的数据点: {data_points_count}

## 任务
评估是否需要调整大纲。可能的调整包括：
1. 新增章节（发现了重要的新方向）
2. 删除章节（发现某方向信息太少）
3. 调整章节顺序或优先级
4. 细化或合并章节

输出JSON格式：
```json
{{
    "needs_revision": true或false,
    "revision_reason": "调整原因",
    "revised_outline": [...],  // 如果needs_revision为true
    "new_search_queries": ["新增的搜索关键词"]  // 如果需要补充搜索
}}
```"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        """Run initial planning, preserving the current state interface."""
        query = state.query.strip()
        if not query:
            raise ValueError("研究问题不能为空")

        state.phase = "planning"
        state.planner_diagnostics = []
        result: dict[str, Any] = {}
        validated_outline: list[dict[str, Any]] | None = None
        prompt = self.PLANNING_PROMPT.format(query=query)
        diagnostics: list[dict[str, Any]] = []
        last_validation_error = "规划响应不符合预期格式"
        for attempt in range(3):
            payload = {"query": query}
            started = time.perf_counter()
            try:
                result, raw_response = await self._complete_planning_json(payload, prompt)
            except Exception as exc:
                diagnostic = self._attempt_diagnostic(
                    attempt=attempt + 1,
                    result=None,
                    raw_response=str(getattr(exc, "response_preview", "")),
                    duration_ms=(time.perf_counter() - started) * 1000,
                    validation_error=f"模型调用或 JSON 解析失败：{exc}",
                    accepted=False,
                )
                diagnostics.append(diagnostic)
                state.planner_diagnostics = diagnostics
                last_validation_error = diagnostic["validation_error"]
                if attempt < 2:
                    prompt = self.PLANNING_RETRY_PROMPT.format(
                        query=query,
                        validation_error=last_validation_error,
                    )
                    continue
                state.errors.append(
                    "Planner 三次尝试均未能生成有效研究计划；"
                    f"最后一次失败原因：{last_validation_error}"
                )
                return state

            response_result = result
            if result.get("sec_1_title") and not result.get("outline"):
                result = self._convert_flat_to_outline(result, query=query)
            outline_value = result.get("outline")
            validation_error = ""
            try:
                if not isinstance(outline_value, list):
                    raise ValueError("响应缺少 outline，且未识别到参考工程扁平章节字段")
                if not 3 <= len(outline_value) <= 8:
                    raise ValueError(f"章节数为 {len(outline_value)}，要求 3 到 8 个章节")
                validated_outline = self._validate_outline(outline_value)
                self._validate_topic_alignment(query, result, validated_outline)
            except ValueError as exc:
                validated_outline = None
                validation_error = str(exc)
                last_validation_error = validation_error

            diagnostics.append(
                self._attempt_diagnostic(
                    attempt=attempt + 1,
                    result=response_result,
                    raw_response=raw_response,
                    duration_ms=(time.perf_counter() - started) * 1000,
                    validation_error=validation_error,
                    accepted=validated_outline is not None,
                )
            )
            state.planner_diagnostics = diagnostics
            if validated_outline is not None:
                break
            if attempt < 2:
                prompt = self.PLANNING_RETRY_PROMPT.format(
                    query=query,
                    validation_error=last_validation_error,
                )

        if validated_outline is None or len(validated_outline) < 3:
            state.errors.append(
                "Planner 三次尝试均未通过大纲校验；"
                f"最后一次拒绝原因：{last_validation_error}"
            )
            return state

        state.outline = validated_outline
        state.hypotheses = self._validate_hypotheses(result.get("hypotheses", []))
        state.research_questions = self._validate_questions(result.get("research_questions", []))
        state.key_entities = self._validate_key_entities(result.get("key_entities", []))
        state.mind_map = result.get("mind_map", {})
        state.knowledge_graph = {"nodes": [], "edges": []}
        return state

    async def _complete_planning_json(
        self,
        payload: dict[str, Any],
        prompt: str,
    ) -> tuple[dict[str, Any], str]:
        """Use exact provider response text when available; support legacy clients."""

        method = getattr(self.llm, "complete_json_with_raw", None)
        if callable(method):
            result, raw_response = await method(
                role=self.name,
                payload=payload,
                system_prompt=self.PLANNING_SYSTEM,
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=16000,
            )
            if not isinstance(result, dict):
                raise ValueError("Planner 的 JSON 根节点必须是对象")
            return result, str(raw_response)

        result = await self._complete_json(
            payload,
            system_prompt=self.PLANNING_SYSTEM,
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=16000,
        )
        return result, json.dumps(result, ensure_ascii=False, default=str)

    def _attempt_diagnostic(
        self,
        *,
        attempt: int,
        result: dict[str, Any] | None,
        raw_response: str,
        duration_ms: float,
        validation_error: str,
        accepted: bool,
    ) -> dict[str, Any]:
        outline = result.get("outline") if isinstance(result, dict) else None
        if isinstance(outline, list):
            section_count = len(outline)
            response_format = "nested_outline"
        elif isinstance(result, dict) and result.get("sec_1_title"):
            section_count = sum(
                1 for index in range(1, 10) if result.get(f"sec_{index}_title")
            )
            response_format = "reference_flat"
        else:
            section_count = 0
            response_format = "unknown"
        model = "unknown"
        settings = getattr(self.llm, "settings", None)
        if settings is not None and callable(getattr(settings, "for_agent", None)):
            try:
                model = str(settings.for_agent(self.name).model)
            except Exception:
                pass
        configured_key = str(getattr(settings, "api_key", "") or "")
        redacted_response = self._redact_sensitive_text(raw_response, configured_key)
        safe_validation_error = self._redact_sensitive_text(
            validation_error, configured_key
        )
        return {
            "agent": self.name,
            "attempt": attempt,
            "model": model,
            "duration_ms": round(duration_ms, 2),
            "response_format": response_format,
            "section_count": section_count,
            "accepted": accepted,
            "validation_error": safe_validation_error[:1000],
            "response_preview": redacted_response[:12000],
            "response_truncated": len(redacted_response) > 12000,
        }

    @staticmethod
    def _redact_sensitive_text(value: str, configured_key: str = "") -> str:
        if configured_key:
            value = value.replace(configured_key, "[redacted-api-key]")
        value = re.sub(
            r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+",
            r"\1[redacted-token]",
            value,
        )
        value = re.sub(
            r"(?i)(api[_-]?key[\"']?\s*[=:]\s*[\"']?)[^\s,\"'}]+",
            r"\1[redacted-api-key]",
            value,
        )
        value = re.sub(
            r"(?i)((?:access[_-]?token|refresh[_-]?token|password|secret|authorization)"
            r"[\"']?\s*[=:]\s*[\"']?)[^\s,\"'}]+",
            r"\1[redacted-secret]",
            value,
        )
        return re.sub(r"\bsk-[A-Za-z0-9_-]{8,}\b", "[redacted-token]", value)

    async def revise(self, state: ResearchState) -> ResearchState:
        """Check whether evidence justifies changing the current outline."""

        if not state.query.strip() or not state.outline:
            return state
        new_findings = [
            f"- {str(fact.get('content', '')).strip()[:100]}"
            for fact in state.facts[-10:]
            if str(fact.get("content", "")).strip()
        ]
        if not new_findings:
            return state
        payload = {
            "query": state.query,
            "current_outline": state.outline,
            "new_findings": "\n".join(new_findings),
            "completed_sections": sum(section.get("status") == "final" for section in state.outline),
            "facts_count": len(state.facts),
            "data_points_count": len(state.data_points),
        }
        result = await self._complete_json(
            payload,
            system_prompt=self.REVISION_SYSTEM,
            user_prompt=self.REVISION_PROMPT.format(**payload),
            temperature=0.3,
            max_tokens=16000,
        )
        if result.get("needs_revision") and result.get("revised_outline"):
            state.outline = self._validate_outline(result["revised_outline"])
        return state

    run_revision = revise

    @staticmethod
    def _validate_topic_alignment(
        query: str,
        result: dict[str, Any],
        outline: list[dict[str, Any]],
    ) -> None:
        """Reject a model plan that cannot be tied to the user's topic."""

        raw_subject = result.get("research_subject")
        if not isinstance(raw_subject, str) or not raw_subject.strip():
            raise ValueError("规划结果缺少可追溯到用户问题的核心研究对象")

        subject = raw_subject.strip()
        normalized_subject = PlannerAgent._normalize_topic_text(subject)
        normalized_query = PlannerAgent._normalize_topic_text(query)
        inferred_subject = PlannerAgent._infer_research_subject(query)
        normalized_inferred = PlannerAgent._normalize_topic_text(inferred_subject)
        subject_is_verbatim = bool(
            normalized_subject and normalized_subject in normalized_query
        )
        subject_contains_inferred = bool(
            normalized_inferred
            and len(normalized_inferred) >= 2
            and normalized_inferred in normalized_subject
        )
        if not normalized_subject or not (subject_is_verbatim or subject_contains_inferred):
            expected_subject = inferred_subject or "可识别的核心对象"
            raise ValueError(
                f"研究对象“{subject}”无法追溯到用户问题中的核心对象“{expected_subject}”"
            )

        # Anchor the plan to the user's inferred leading subject when possible.
        # A model may describe it together with industry/time-span context, but
        # those extra words must not become independent topic anchors.
        anchor_subject = inferred_subject if subject_contains_inferred else subject
        anchors = PlannerAgent._subject_anchors(anchor_subject)
        anchors.extend(PlannerAgent._related_query_anchors(query))
        anchors = list(dict.fromkeys(anchors))
        section_hits = 0
        total_queries = 0
        query_hits = 0
        for section in outline:
            section_text = " ".join(
                [
                    str(section.get("title", "")),
                    str(section.get("description", "")),
                ]
            ).casefold()
            search_queries = section.get("search_queries", [])
            if not isinstance(search_queries, list):
                search_queries = [search_queries]
            search_text = " ".join(str(item) for item in search_queries).casefold()
            if any(anchor in section_text or anchor in search_text for anchor in anchors):
                section_hits += 1
            for search_query in search_queries:
                total_queries += 1
                if any(anchor in str(search_query).casefold() for anchor in anchors):
                    query_hits += 1

        # The reference Architect does not demand the same entity string in every
        # sentence or search query. Require enough topic anchors to reject a
        # wholesale topic drift, while allowing chapter-specific terminology.
        # A small number of matching keywords must not allow the rest of the
        # outline to drift to another topic. Two thirds leaves room for
        # chapters expressed through related terms (for example, a biography's
        # historical context) while rejecting plans where most sections are
        # unrelated.
        min_section_hits = max(1, math.ceil(len(outline) * 2 / 3))
        min_query_hits = max(1, math.ceil(max(total_queries, 1) * 2 / 3))
        if section_hits < min_section_hits:
            raise ValueError(
                "大纲章节与核心研究对象的关联不足："
                f"仅 {section_hits}/{len(outline)} 个章节出现对象名或名称片段"
            )
        if query_hits < min_query_hits:
            raise ValueError(
                "搜索词与核心研究对象关联不足："
                f"仅 {query_hits}/{total_queries} 条查询出现对象名或名称片段"
            )

    @staticmethod
    def _subject_anchors(subject: str) -> list[str]:
        """Return the full subject and useful two-character fragments."""

        value = re.sub(r"\s+", "", subject).casefold()
        anchors = [value] if value else []
        cjk = "".join(re.findall(r"[\u4e00-\u9fff]", value))
        if len(cjk) >= 3:
            anchors.extend(cjk[index : index + 2] for index in range(len(cjk) - 1))
        return list(dict.fromkeys(anchor for anchor in anchors if len(anchor) >= 2))

    @staticmethod
    def _related_query_anchors(query: str) -> list[str]:
        """Keep explicit industry/domain phrases near the named research object."""

        anchors: list[str] = []
        for match in re.finditer(
            r"(?:所在|所属|相关的?|聚焦于)([\u4e00-\u9fff]{2,12}"
            r"(?:行业|产业|领域|市场|流派|群体))",
            query,
        ):
            phrase = match.group(1)
            anchors.append(phrase.casefold())
            suffix = re.search(r"(?:行业|产业|领域|市场|流派|群体)$", phrase)
            if suffix:
                base = phrase[: suffix.start()]
                if len(base) >= 2:
                    anchors.append(base.casefold())
        return list(dict.fromkeys(anchors))

    @staticmethod
    def _normalize_topic_text(value: str) -> str:
        return re.sub(r"[\s\W_]+", "", value, flags=re.UNICODE).casefold()

    @staticmethod
    def _infer_research_subject(query: str) -> str:
        """Infer the subject for reference-style flat responses without the field."""

        value = query.strip()
        value = re.sub(
            r"^(?:(?:请问|请|麻烦|帮我|我想(?:要)?|请你)\s*)?"
            r"(?:介绍一下|介绍|分析|研究|梳理|调查|评估|总结|说明|解释|回顾|撰写|写一份|写|谈谈|看看)\s*",
            "",
            value,
        )
        # A flat ChiefArchitect response has no subject key. Take the leading
        # object phrase from the original question, stopping before the requested
        # time window, relation, or report dimensions.
        value = re.split(
            r"(?:所在|近\s*(?:\d+|几|多)?年|过去|最近|同期|期间|的发展|的历史|的生平|的一生|的|在|于|关于|\b20\d{2}\b|[，,。；;])",
            value,
            maxsplit=1,
        )[0]
        value = value.strip(" ：:、\t\r\n")
        if len(value) < 2 or value in {"公司", "行业", "市场", "企业", "人物"}:
            return ""
        return value[:40]

    @staticmethod
    def _convert_flat_to_outline(
        flat_result: dict[str, Any],
        *,
        query: str = "",
    ) -> dict[str, Any]:
        """Convert the reference architect's flat fields to state fields."""
        outline: list[dict[str, Any]] = []
        for index in range(1, 10):
            title = flat_result.get(f"sec_{index}_title")
            if title is None:
                break
            title = str(title).strip()
            description = str(flat_result.get(f"sec_{index}_desc", "")).strip()
            search_query = str(flat_result.get(f"sec_{index}_query", title)).strip()
            outline.append({
                "id": f"sec_{index}",
                "title": title or f"章节{index}",
                "description": description,
                "section_type": "mixed",
                "requires_data": bool(
                    flat_result.get(f"sec_{index}_requires_data", index <= 2)
                ),
                "requires_chart": bool(
                    flat_result.get(f"sec_{index}_requires_chart", index <= 2)
                ),
                "priority": index,
                "search_queries": [search_query or title or f"章节{index}"],
            })
        questions = flat_result.get("questions", [])
        if isinstance(questions, str):
            questions = [item.strip() for item in questions.split(";") if item.strip()]
        elif not isinstance(questions, list):
            questions = []
        hypotheses: list[dict[str, Any]] = []
        for index in range(1, 6):
            content = str(flat_result.get(f"hypothesis_{index}", "")).strip()
            if content:
                hypotheses.append({
                    "id": f"h_{index}",
                    "content": content,
                    "status": "unverified",
                    "evidence_for": [],
                    "evidence_against": [],
                })
        converted = {
            "outline": outline,
            "research_questions": questions,
            "hypotheses": hypotheses,
            "key_entities": flat_result.get("key_entities", []),
            "mind_map": flat_result.get("mind_map", {}),
        }
        research_subject = flat_result.get("research_subject")
        if not isinstance(research_subject, str) or not research_subject.strip():
            research_subject = PlannerAgent._infer_research_subject(query)
        if research_subject:
            converted["research_subject"] = research_subject
        return converted

    @staticmethod
    def _validate_outline(value: Any) -> list[dict[str, Any]]:
        """Normalize sections while preserving the reference defaults."""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 outline 必须是非空列表")

        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个章节不是对象")
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            section_type = str(item.get("section_type", "mixed")).strip() or "mixed"
            if section_type not in {"qualitative", "quantitative", "mixed"}:
                section_type = "mixed"

            status = str(item.get("status", "pending")).strip() or "pending"
            if status not in {"pending", "researching", "drafted", "reviewed", "final"}:
                status = "pending"

            search_queries = item.get("search_queries", [title])
            if not isinstance(search_queries, list):
                search_queries = [search_queries]
            search_queries = [str(query).strip() for query in search_queries if str(query).strip()]
            if not search_queries:
                search_queries = [title]

            try:
                priority = int(item.get("priority", index))
            except (TypeError, ValueError):
                priority = index
            section = Section(
                id=str(item.get("id", f"sec_{index}")).strip() or f"sec_{index}",
                title=title,
                description=description,
                section_type=section_type,
                status=status,
                requires_data=bool(item.get("requires_data", False)),
                requires_chart=bool(item.get("requires_chart", False)),
                priority=priority,
                search_queries=search_queries,
            )
            validated.append(section.to_dict())
        return validated

    @staticmethod
    def _validate_hypotheses(value: Any) -> list[dict[str, Any]]:
        """Normalize valid hypotheses and ignore optional malformed entries."""
        if value is None:
            return []
        if not isinstance(value, list):
            return []

        validated: list[dict[str, Any]] = []
        allowed_statuses = {
            "unverified",
            "supported",
            "refuted",
            "partially_supported",
        }
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            status = str(item.get("status", "unverified")).strip() or "unverified"
            if status not in allowed_statuses:
                status = "unverified"

            evidence_for = item.get("evidence_for", [])
            evidence_against = item.get("evidence_against", [])
            if not isinstance(evidence_for, list):
                evidence_for = []
            if not isinstance(evidence_against, list):
                evidence_against = []

            hypothesis = Hypothesis(
                id=str(item.get("id", f"h_{index}")).strip() or f"h_{index}",
                content=content,
                status=status,
                evidence_for=[str(evidence).strip() for evidence in evidence_for if str(evidence).strip()],
                evidence_against=[
                    str(evidence).strip() for evidence in evidence_against if str(evidence).strip()
                ],
            )
            validated.append(hypothesis.to_dict())
        return validated

    @staticmethod
    def _validate_key_entities(value: Any) -> list[str]:
        """Normalize string or named entity objects to names."""
        if value is None:
            return []
        if not isinstance(value, list):
            return []

        entities: list[str] = []
        for item in value:
            if isinstance(item, dict):
                item = item.get("name", "")
            name = str(item).strip()
            if name:
                entities.append(name)
        return entities

    @staticmethod
    def _validate_questions(value: Any) -> list[str]:
        """Normalize semicolon-delimited or list research questions."""
        if isinstance(value, str):
            value = [item.strip() for item in value.split(";") if item.strip()]
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]
