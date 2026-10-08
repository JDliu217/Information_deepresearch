"""Research planning agent.

The planning contract follows the reference V2 architect flow: the model is
asked for a compact, flat JSON plan first and the agent converts it into the
structured outline used by this project's LangGraph state.
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
        "你是一位专业的行业研究规划师。请严格按照要求的 JSON 格式输出，"
        "不要添加任何额外内容。"
    )
    PLANNING_PROMPT = r"""研究课题：{query}

请为该课题生成研究大纲和研究假设，输出JSON格式如下：

{{
  "hypothesis_1": "关于市场/行业趋势的假设（需要验证）",
  "hypothesis_2": "关于竞争格局或技术发展的假设（需要验证）",
  "hypothesis_3": "关于政策或外部因素影响的假设（需要验证）",
  "sec_1_title": "市场概况",
  "sec_1_desc": "描述市场规模、增速",
  "sec_1_query": "搜索关键词",
  "sec_2_title": "竞争格局",
  "sec_2_desc": "描述主要企业",
  "sec_2_query": "搜索关键词",
  "sec_3_title": "技术趋势",
  "sec_3_desc": "描述核心技术",
  "sec_3_query": "搜索关键词",
  "sec_4_title": "政策环境",
  "sec_4_desc": "描述相关政策",
  "sec_4_query": "搜索关键词",
  "sec_5_title": "挑战机遇",
  "sec_5_desc": "描述挑战和机会",
  "sec_5_query": "搜索关键词",
  "sec_6_title": "未来展望",
  "sec_6_desc": "描述发展趋势",
  "sec_6_query": "搜索关键词",
  "questions": "核心问题1;核心问题2;核心问题3"
}}

研究假设示例：
- 假设市场规模将持续增长，需要用数据验证增速
- 假设某类技术会成为主流，需要找证据支持或反驳
- 假设政策变化会影响行业格局，需要分析政策走向

请根据研究课题填写具体内容，每个字段都是字符串类型。"""
    PLANNING_RETRY_PROMPT = """请为“{query}”生成研究大纲，只返回 JSON：
{{
  "outline": [
    {{"id":"sec_1","title":"章节标题","description":"章节要回答的问题",
      "section_type":"mixed","requires_data":true,"requires_chart":false,
      "search_queries":["关键词1","关键词2"]}}
  ],
  "research_questions":["问题1","问题2","问题3"],
  "hypotheses":[{{"id":"h_1","content":"待验证假设","status":"unverified"}}],
  "key_entities":[]
}}
要求 outline 包含 5 到 8 个章节，覆盖课题的现状、竞争、技术、政策和未来趋势。"""
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
            if isinstance(result.get("outline"), list) and len(result["outline"]) >= 3:
                break
            if attempt < 2:
                prompt = self.PLANNING_RETRY_PROMPT.format(query=query)

        outline_value = result.get("outline")
        if not isinstance(outline_value, list) or len(outline_value) < 3:
            raise ValueError("Planner 返回的 outline 必须是非空列表，且至少包含 3 个章节")

        state.outline = self._validate_outline(outline_value)
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
            system_prompt=self.PLANNING_SYSTEM,
            user_prompt=self.REVISION_PROMPT.format(**payload),
            temperature=0.3,
            max_tokens=16000,
        )
        if result.get("needs_revision") and result.get("revised_outline"):
            state.outline = self._validate_outline(result["revised_outline"])
        return state

    run_revision = revise

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
                "requires_data": index <= 2,
                "requires_chart": index <= 2,
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
        return {
            "outline": outline,
            "research_questions": questions,
            "hypotheses": hypotheses,
            "key_entities": flat_result.get("key_entities", []),
            "mind_map": flat_result.get("mind_map", {}),
        }

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
