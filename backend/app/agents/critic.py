"""研究报告质量审核 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class CriticAgent(BaseAgent):
    """检查报告是否有事实、来源和基本的可发布条件。"""

    name = "critic"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.final_report.strip():
            raise ValueError("没有可供审核的报告")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "report": state.final_report,
                "facts": state.facts,
                "sources": state.raw_sources,
                "iteration": state.iteration,
                "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
            },
        )
        review = self._validate_review(result)
        state.review_result = review
        state.critic_feedback = [
            {
                "description": issue,
                "resolved": False,
            }
            for issue in review["issues"]
        ]
        state.unresolved_issues = len(state.critic_feedback)
        state.quality_score = review["quality_score"]
        state.phase = "reviewing"
        return state

    @staticmethod
    def _validate_review(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Critic 返回结果必须是对象")

        verdict = str(value.get("verdict", "")).strip()
        if verdict not in {"pass", "needs_revision"}:
            raise ValueError("Critic verdict 必须是 pass 或 needs_revision")

        try:
            quality_score = float(value.get("quality_score"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Critic quality_score 必须是数字") from exc
        if not 0 <= quality_score <= 10:
            raise ValueError("Critic quality_score 必须在 0 到 10 之间")

        issues = value.get("issues", [])
        if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
            raise ValueError("Critic issues 必须是字符串列表")

        needs_more_research = value.get("needs_more_research", False)
        if not isinstance(needs_more_research, bool):
            raise ValueError("Critic needs_more_research 必须是布尔值")

        search_queries = value.get("search_queries", [])
        if not isinstance(search_queries, list) or not all(
            isinstance(query, str) and query.strip() for query in search_queries
        ):
            raise ValueError("Critic search_queries 必须是非空字符串列表")

        return {
            "verdict": verdict,
            "quality_score": quality_score,
            "summary": str(value.get("summary", "")).strip(),
            "needs_more_research": needs_more_research,
            "issues": issues,
            "search_queries": [query.strip() for query in search_queries],
        }
