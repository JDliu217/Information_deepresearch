"""研究规划 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Hypothesis, Section
from app.domain.state import ResearchState

from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """把一个用户问题转换成 V2 研究大纲和可验证假设。"""

    name = "planner"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        """调用 LLM，校验结果，然后写回共享状态。"""
        query = state.query.strip()
        if not query:
            raise ValueError("研究问题不能为空")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": query,
                "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
            },
        )
        outline = self._validate_outline(result.get("outline"))
        hypotheses = self._validate_hypotheses(result.get("hypotheses", []))
        research_questions = self._validate_questions(result.get("research_questions"))
        key_entities = self._validate_key_entities(result.get("key_entities", []))

        state.outline = outline
        state.hypotheses = hypotheses
        state.research_questions = research_questions
        state.key_entities = key_entities
        state.mind_map = result.get("mind_map", {})
        state.phase = "planning"
        return state

    @staticmethod
    def _validate_outline(value: Any) -> list[dict[str, Any]]:
        """用 Section 校验并序列化 LLM 返回的章节大纲。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 outline 必须是非空列表")

        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个章节不是对象")
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not title or not description:
                raise ValueError(f"Planner 的第 {index} 个章节缺少 title 或 description")

            section_type = str(item.get("section_type", "mixed")).strip() or "mixed"
            if section_type not in {"qualitative", "quantitative", "mixed"}:
                raise ValueError(f"Planner 的第 {index} 个章节 section_type 无效")

            status = str(item.get("status", "pending")).strip() or "pending"
            if status not in {"pending", "researching", "drafted", "reviewed", "final"}:
                raise ValueError(f"Planner 的第 {index} 个章节 status 无效")

            search_queries = item.get("search_queries", [title])
            if not isinstance(search_queries, list):
                raise ValueError(f"Planner 的第 {index} 个章节 search_queries 必须是列表")
            search_queries = [str(query).strip() for query in search_queries if str(query).strip()]
            if not search_queries:
                search_queries = [title]

            section = Section(
                id=str(item.get("id", f"sec_{index}")).strip() or f"sec_{index}",
                title=title,
                description=description,
                section_type=section_type,
                status=status,
                requires_data=bool(item.get("requires_data", False)),
                requires_chart=bool(item.get("requires_chart", False)),
                priority=int(item.get("priority", index)),
                search_queries=search_queries,
            )
            validated.append(section.to_dict())
        return validated

    @staticmethod
    def _validate_hypotheses(value: Any) -> list[dict[str, Any]]:
        """用 Hypothesis 校验研究假设，并初始化证据列表。"""
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Planner 返回的 hypotheses 必须是列表")

        validated: list[dict[str, Any]] = []
        allowed_statuses = {
            "unverified",
            "supported",
            "refuted",
            "partially_supported",
        }
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个假设不是对象")
            content = str(item.get("content", "")).strip()
            if not content:
                raise ValueError(f"Planner 的第 {index} 个假设缺少 content")
            status = str(item.get("status", "unverified")).strip() or "unverified"
            if status not in allowed_statuses:
                raise ValueError(f"Planner 的第 {index} 个假设 status 无效")

            hypothesis = Hypothesis(
                id=str(item.get("id", f"h_{index}")).strip() or f"h_{index}",
                content=content,
                status=status,
                evidence_for=[str(evidence).strip() for evidence in item.get("evidence_for", [])],
                evidence_against=[
                    str(evidence).strip() for evidence in item.get("evidence_against", [])
                ],
            )
            validated.append(hypothesis.to_dict())
        return validated

    @staticmethod
    def _validate_key_entities(value: Any) -> list[str]:
        """兼容字符串或带 name 的实体对象，并统一成名称列表。"""
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Planner 返回的 key_entities 必须是列表")

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
        """确保子问题是非空字符串列表。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 research_questions 必须是非空列表")

        questions = [str(item).strip() for item in value]
        if any(not question for question in questions):
            raise ValueError("Planner 返回了空的研究子问题")
        return questions
