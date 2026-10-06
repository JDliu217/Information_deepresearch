"""研究规划 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """把一个用户问题拆成可执行的研究计划。"""

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
        plan = self._validate_plan(result.get("plan"))
        research_questions = self._validate_questions(result.get("research_questions"))

        state.plan = plan
        state.research_questions = research_questions
        state.phase = "planning"
        return state

    @staticmethod
    def _validate_plan(value: Any) -> list[dict[str, str]]:
        """确保计划是由标题和描述组成的字典列表。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 plan 必须是非空列表")

        validated: list[dict[str, str]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个计划不是对象")
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not title or not description:
                raise ValueError(f"Planner 的第 {index} 个计划缺少 title 或 description")
            validated.append({"title": title, "description": description})
        return validated

    @staticmethod
    def _validate_questions(value: Any) -> list[str]:
        """确保子问题是非空字符串列表。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 research_questions 必须是非空列表")

        questions = [str(item).strip() for item in value]
        if any(not question for question in questions):
            raise ValueError("Planner 返回了空的研究子问题")
        return questions
