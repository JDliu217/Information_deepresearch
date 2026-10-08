"""Research planning agent.

The planner asks the model for a topic-specific JSON plan and validates its
declared subject before passing the outline to the search stage. Reference-style
flat responses are accepted only when they provide enough topic context.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Hypothesis, Section
from app.domain.state import ResearchState

from .base import BaseAgent


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
1. 生成5-8个相互衔接的章节，章节结构要由当前研究对象和问题决定。人物研究可按生平阶段、时代背景、作品或影响组织；只有在用户问题确实涉及这些方面时才采用。
2. research_subject填写用户问题中直接出现的核心对象名称，不要翻译、替换或另选对象。每个章节都要明确回答研究问题的一部分；章节描述和搜索词都要围绕该对象，搜索词必须包含对象名称和本章要查的具体方面。
3. 不要仅因为某类内容常见就加入无关的行业、组织、技术或政策分析。
4. 只有研究问题需要可量化证据时才设置 requires_data=true；只有存在可比较的数据且图表有帮助时才设置 requires_chart=true。定性研究应将二者设为 false。
5. 提出3-5个能由研究材料回答的具体问题。只有适合验证假设的课题才填写 hypotheses；描述性课题可以返回空列表，不要强造市场或趋势假设。
6. 不要在规划阶段编造事实、数据或来源。

## 输出格式
只返回一个 JSON 对象，格式如下：
{{
  "research_subject": "问题中的核心研究对象",
  "outline": [
    {{
      "id": "sec_1",
      "title": "与研究对象相关的章节标题",
      "description": "本章节需要回答的问题和覆盖范围",
      "section_type": "qualitative、quantitative 或 mixed",
      "requires_data": false,
      "requires_chart": false,
      "search_queries": ["包含核心研究对象的具体搜索词"]
    }}
  ],
  "research_questions": ["具体研究问题"],
  "hypotheses": [],
  "key_entities": [],
  "mind_map": {{}}
}}

outline必须有5-8章。所有章节、研究问题、假设和搜索词都必须与用户的研究问题直接相关。不要输出示例主题或模板占位文字。"""
    PLANNING_RETRY_PROMPT = """请重新为以下用户问题制定研究计划：
{query}

先识别问题中的核心研究对象和目标，再生成5-8个与该主题直接相关的章节。不要改写成其他主题，不要套用固定领域的大纲；每个章节描述和搜索词都要围绕核心对象，搜索词应包含核心对象名称和要查的具体方面。只在确有需要时设置数据、图表和研究假设。

严格返回 JSON：
{{"research_subject": "问题中的核心研究对象", "outline": [
    {{"id": "sec_1", "title": "章节标题", "description": "章节要回答的问题", "section_type": "qualitative", "requires_data": false, "requires_chart": false, "search_queries": ["对象名称+具体问题"]}}
], "research_questions": ["问题1", "问题2", "问题3"], "key_entities": []}}

outline必须包含5-8个章节，不能包含与用户问题无关的主题。"""
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

        result: dict[str, Any] = {}
        validated_outline: list[dict[str, Any]] | None = None
        prompt = self.PLANNING_PROMPT.format(query=query)
        for attempt in range(3):
            payload = {"query": query}
            result = await self._complete_json(
                payload,
                system_prompt=self.PLANNING_SYSTEM,
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=16000,
            )
            if result.get("sec_1_title") and not result.get("outline"):
                result = self._convert_flat_to_outline(result)
            outline_value = result.get("outline")
            if isinstance(outline_value, list) and len(outline_value) >= 3:
                try:
                    validated_outline = self._validate_outline(outline_value)
                    self._validate_topic_alignment(query, result, validated_outline)
                except ValueError:
                    validated_outline = None
                if validated_outline is not None and len(validated_outline) >= 3:
                    break
            if attempt < 2:
                prompt = self.PLANNING_RETRY_PROMPT.format(query=query)

        if validated_outline is None or len(validated_outline) < 3:
            state.errors.append("Failed to generate research plan after retries")
            return state

        state.outline = validated_outline
        state.hypotheses = self._validate_hypotheses(result.get("hypotheses", []))
        state.research_questions = self._validate_questions(result.get("research_questions", []))
        state.key_entities = self._validate_key_entities(result.get("key_entities", []))
        state.mind_map = result.get("mind_map", {})
        state.knowledge_graph = {"nodes": [], "edges": []}
        state.phase = "planning"
        return state

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
            raise ValueError("Planner 缺少 research_subject，无法校验研究主题")

        subject = raw_subject.strip()
        if subject.casefold() not in query.casefold():
            raise ValueError("Planner 的 research_subject 不在用户问题中")

        for index, section in enumerate(outline, start=1):
            description = str(section.get("description", ""))
            if subject.casefold() not in description.casefold():
                raise ValueError(
                    f"Planner 第 {index} 个章节描述没有明确关联核心研究对象"
                )
            search_queries = section.get("search_queries", [])
            if not search_queries or not all(
                subject.casefold() in str(search_query).casefold()
                for search_query in search_queries
            ):
                raise ValueError(
                    f"Planner 第 {index} 个章节的搜索词没有围绕核心研究对象"
                )

    @staticmethod
    def _convert_flat_to_outline(flat_result: dict[str, Any]) -> dict[str, Any]:
        """Convert the reference architect's flat fields to state fields."""
        outline: list[dict[str, Any]] = []
        for index in range(1, 10):
            title = flat_result.get(f"sec_{index}_title")
            if title is None:
                break
            title = str(title).strip()
            description = str(flat_result.get(f"sec_{index}_desc", "")).strip()
            query = str(flat_result.get(f"sec_{index}_query", title)).strip()
            outline.append({
                "id": f"sec_{index}",
                "title": title or f"章节{index}",
                "description": description,
                "section_type": "mixed",
                "requires_data": bool(flat_result.get(f"sec_{index}_requires_data", False)),
                "requires_chart": bool(flat_result.get(f"sec_{index}_requires_chart", False)),
                "priority": index,
                "search_queries": [query or title or f"章节{index}"],
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
        if "research_subject" in flat_result:
            converted["research_subject"] = flat_result["research_subject"]
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
