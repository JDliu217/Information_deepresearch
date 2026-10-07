"""研究报告质量审核 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import CriticFeedback, FactCheckResult, ReviewResult
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
                "data_points": state.data_points,
                "insights": state.insights,
                "charts": state.charts,
                "code_executions": state.code_executions,
                "iteration": state.iteration,
                "instruction": "检查事实和数据洞察是否有来源支撑，并判断报告是否需要补充研究。",
            },
        )
        review = self._validate_review(result, state)
        state.review_result = review
        state.critic_feedback = review["structured_issues"]
        state.unresolved_issues = len(
            [
                issue
                for issue in state.critic_feedback
                if issue.get("severity") in {"critical", "major"}
            ]
        )
        state.quality_score = review["quality_score"]
        state.phase = "reviewing"
        return state

    @staticmethod
    def _validate_review(value: Any, state: ResearchState | None = None) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Critic 返回结果必须是对象")

        assessment = value.get("overall_assessment", {})
        if assessment is None:
            assessment = {}
        if not isinstance(assessment, dict):
            raise ValueError("Critic overall_assessment 必须是对象")

        verdict = str(assessment.get("verdict", value.get("verdict", ""))).strip()
        if verdict not in {"pass", "needs_revision", "major_issues"}:
            raise ValueError("Critic verdict 必须是 pass、needs_revision 或 major_issues")

        try:
            quality_score = float(
                assessment.get("quality_score", value.get("quality_score"))
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Critic quality_score 必须是数字") from exc
        if not 0 <= quality_score <= 10:
            raise ValueError("Critic quality_score 必须在 0 到 10 之间")

        issues = CriticAgent._validate_issues(value.get("issues", []))

        fact_checks = value.get("fact_check_results", [])
        if not isinstance(fact_checks, list):
            raise ValueError("Critic fact_check_results 必须是列表")
        normalized_fact_checks = []
        for index, item in enumerate(fact_checks, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Critic 的第 {index} 个事实核查结果不是对象")
            fact_id = str(item.get("fact_id", "")).strip()
            status = str(item.get("status", "")).strip()
            if not fact_id or status not in {"verified", "unverified", "suspicious", "false"}:
                raise ValueError(f"Critic 的第 {index} 个事实核查结果无效")
            normalized_fact_checks.append(
                FactCheckResult(
                    fact_id=fact_id,
                    status=status,
                    reason=str(item.get("reason", "")).strip(),
                ).to_dict()
            )

        missing_aspects = CriticAgent._validate_string_list(
            value.get("missing_aspects", []), "missing_aspects"
        )
        strengths = CriticAgent._validate_string_list(value.get("strengths", []), "strengths")

        needs_more_research = value.get("needs_more_research", False)
        if not isinstance(needs_more_research, bool):
            raise ValueError("Critic needs_more_research 必须是布尔值")

        search_queries = value.get("search_queries", [])
        if not isinstance(search_queries, list) or not all(
            isinstance(query, str) and query.strip() for query in search_queries
        ):
            raise ValueError("Critic search_queries 必须是非空字符串列表")

        summary = str(assessment.get("summary", value.get("summary", ""))).strip()
        return ReviewResult(
            verdict=verdict,
            quality_score=quality_score,
            summary=summary,
            issues=[issue["description"] for issue in issues],
            structured_issues=issues,
            fact_check_results=normalized_fact_checks,
            missing_aspects=missing_aspects,
            strengths=strengths,
            needs_more_research=needs_more_research,
            search_queries=[query.strip() for query in search_queries],
        ).to_dict()

    @staticmethod
    def _validate_string_list(value: Any, field_name: str) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValueError(f"Critic {field_name} 必须是字符串列表")
        return [item.strip() for item in value]

    @staticmethod
    def _validate_issues(value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Critic issues 必须是对象列表")

        normalized = []
        allowed_types = {
            "missing_source",
            "logic_error",
            "bias",
            "hallucination",
            "outdated",
            "incomplete",
        }
        allowed_severity = {"critical", "major", "minor"}
        for index, item in enumerate(value, start=1):
            if isinstance(item, str):
                description = item.strip()
                if not description:
                    raise ValueError(f"Critic 的第 {index} 个问题不能为空")
                item = {
                    "id": f"issue_{index}",
                    "target_section": "global",
                    "issue_type": "incomplete",
                    "severity": "major",
                    "description": description,
                    "suggestion": description,
                }
            if not isinstance(item, dict):
                raise ValueError(f"Critic 的第 {index} 个问题不是对象")
            issue_id = str(item.get("id", f"issue_{index}")).strip() or f"issue_{index}"
            target_section = str(item.get("target_section", "global")).strip() or "global"
            issue_type = str(item.get("issue_type", "incomplete")).strip()
            severity = str(item.get("severity", "minor")).strip()
            description = str(item.get("description", "")).strip()
            suggestion = str(item.get("suggestion", "")).strip()
            if issue_type not in allowed_types:
                raise ValueError(f"Critic 的第 {index} 个问题 issue_type 无效")
            if severity not in allowed_severity:
                raise ValueError(f"Critic 的第 {index} 个问题 severity 无效")
            if not description or not suggestion:
                raise ValueError(f"Critic 的第 {index} 个问题缺少 description 或 suggestion")
            normalized.append(
                CriticFeedback(
                    id=issue_id,
                    target_section=target_section,
                    issue_type=issue_type,
                    severity=severity,
                    description=description,
                    suggestion=suggestion,
                    location=str(item.get("location", "")).strip(),
                    evidence=str(item.get("evidence", "")).strip(),
                    requires_new_search=bool(item.get("requires_new_search", False)),
                    search_query=str(item.get("search_query", "")).strip(),
                    resolved=bool(item.get("resolved", False)),
                ).to_dict()
            )
        return normalized
