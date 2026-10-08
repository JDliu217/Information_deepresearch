"""研究报告质量审核 Agent。"""

from __future__ import annotations

import re
import uuid
from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import CriticFeedback, FactCheckResult, ReviewResult
from app.domain.state import ResearchState

from .base import BaseAgent


class CriticAgent(BaseAgent):
    """检查报告是否有事实、来源和基本的可发布条件。"""

    name = "critic"
    REVIEW_SYSTEM = "你是一位极其严苛的质量审核专家，专门找出研究报告中的问题。你永远不会轻易满意。"
    REVIEW_PROMPT = r"""你是一位极其严苛的学术审稿人和事实核查专家。你的任务是找出研究报告中的所有问题。

## 审核原则（必须严格执行）
1. **零容忍幻觉**：任何没有明确来源的数据或事实，都是问题
2. **逻辑闭环**：论点必须有论据支撑，论据必须有来源
3. **偏见警惕**：单方面观点、情绪化表达都是问题
4. **时效性**：过时的数据（超过2年）必须标注
5. **完整性**：是否遗漏重要方面

## 研究问题
{query}

## 研究大纲
{outline}

## 待审核内容

### 章节草稿
{draft_content}

### 引用的事实
{facts}

### 使用的数据点
{data_points}

## 任务
逐条审核上述内容，找出所有问题。你必须扮演一个"找茬专家"的角色。

## 输出格式
```json
{{
    "overall_assessment": {{
        "quality_score": 1-10,
        "verdict": "pass/needs_revision/major_issues",
        "summary": "整体评估摘要"
    }},
    "issues": [
        {{
            "id": "issue_1",
            "target_section": "章节ID或'全局'",
            "issue_type": "missing_source/logic_error/bias/hallucination/outdated/incomplete",
            "severity": "critical/major/minor",
            "location": "具体位置描述",
            "description": "问题详细描述",
            "evidence": "为什么这是问题的证据",
            "suggestion": "具体的修改建议",
            "requires_new_search": true或false,
            "search_query": "如果需要补充搜索，建议的关键词"
        }}
    ],
    "fact_check_results": [
        {{
            "fact_id": "事实ID",
            "status": "verified/unverified/suspicious/false",
            "reason": "判断理由"
        }}
    ],
    "missing_aspects": ["报告中遗漏的重要方面"],
    "strength_points": ["报告中做得好的地方"]
}}
```

## 严重程度说明
- critical: 必须修复，否则报告不可用（如：核心数据错误、严重幻觉）
- major: 强烈建议修复，影响报告质量（如：缺少来源、逻辑漏洞）
- minor: 建议修复，提升报告质量（如：表述不够精确）

## 评分标准（1-10分制）
- 9-10分：优秀，几乎无问题，可直接发布
- 7-8分：良好，有小问题但不影响整体质量，审核通过（verdict=pass）
- 5-6分：一般，有明显问题需要修订
- 3-4分：较差，问题较多，需要大幅修改
- 1-2分：很差，存在严重问题或大量错误

注意：quality_score >= 7 时才能设置 verdict 为 "pass"

开始你的审核："""
    FINAL_CHECK_SYSTEM = "你是最终质量把关人。"
    FINAL_CHECK_PROMPT = r"""你是最终质量把关人。这是修订后的研究报告。

## 原始问题
{query}

## 之前的问题
{previous_issues}

## 修订后的内容
{revised_content}

## 任务
检查之前的问题是否已解决，是否有新问题产生。

输出JSON：
```json
{{
    "resolved_issues": ["已解决的问题ID列表"],
    "unresolved_issues": ["未解决的问题ID列表"],
    "new_issues": [{{
        "description": "新发现的问题",
        "severity": "critical/major/minor"
    }}],
    "final_verdict": "approved/needs_more_work",
    "final_score": 1-10,
    "publication_readiness": "ready/almost_ready/not_ready",
    "final_comments": "最终评语"
}}
```"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.final_report.strip():
            raise ValueError("没有可供审核的报告")

        payload = self._build_review_context(state)
        result = await self._complete_json(
            payload,
            system_prompt=self.REVIEW_SYSTEM,
            user_prompt=self.REVIEW_PROMPT.format(
                query=payload["query"],
                outline=payload["outline_text"],
                draft_content=payload["draft_content"],
                facts=payload["facts_text"],
                data_points=payload["data_points_text"],
            ),
            temperature=0.2,
            max_tokens=16000,
        )
        review = self._validate_review(result, state)
        state.review_result = review
        new_feedback = []
        for issue in review["structured_issues"]:
            issue = dict(issue)
            issue["id"] = f"issue_{uuid.uuid4().hex[:8]}"
            issue["resolved"] = False
            new_feedback.append(issue)
        state.critic_feedback.extend(new_feedback)
        state.review_result["structured_issues"] = new_feedback
        state.unresolved_issues = len(
            [
                issue
                for issue in new_feedback
                if issue.get("severity") in {"critical", "major"}
            ]
        )
        state.quality_score = review["quality_score"]
        state.phase = "reviewing"
        return state

    async def final_check(self, state: ResearchState) -> dict[str, Any]:
        """对 Writer 修订后的报告做一次轻量最终检查。

        这是参考 CriticMaster 的最终检查能力，结果不直接改变工作流，
        由调用节点决定是否记录或继续结束。
        """

        previous_issues = [
            f"- [{issue.get('severity')}] {issue.get('description')}"
            for issue in state.critic_feedback
            if isinstance(issue, dict) and not issue.get("resolved")
        ]
        payload = {
            "query": state.query,
            "previous_issues": "\n".join(previous_issues) or "无之前的问题",
            "revised_content": state.final_report[:8000],
        }
        return await self._complete_json(
            payload,
            system_prompt=self.FINAL_CHECK_SYSTEM,
            user_prompt=self.FINAL_CHECK_PROMPT.format(**payload),
            max_tokens=16000,
        )

    @staticmethod
    def route_review(review: dict[str, Any]) -> dict[str, Any]:
        """把审核问题转换成工作流可执行的下一步。"""
        structured_issues = review.get("structured_issues", [])
        queries: list[str] = []
        research_issue_types = {"missing_source", "incomplete", "outdated"}
        missing_aspects = review.get("missing_aspects", [])
        research_issue_count = 0
        for issue in structured_issues:
            if not isinstance(issue, dict):
                continue
            if (
                issue.get("issue_type") in research_issue_types
                and issue.get("severity") in {"critical", "major"}
            ):
                research_issue_count += 1
                query = str(issue.get("search_query", "")).strip()
                if issue.get("requires_new_search") and query:
                    queries.append(query)
        queries.extend(
            aspect.strip()
            for aspect in missing_aspects[:3]
            if isinstance(aspect, str) and aspect.strip()
        )
        total_critical_major = sum(
            1 for issue in structured_issues
            if isinstance(issue, dict) and issue.get("severity") in {"critical", "major"}
        )
        should_research = (
            bool(queries)
            and (research_issue_count > 0 or bool(missing_aspects))
            and (
                total_critical_major == 0
                or research_issue_count / max(total_critical_major, 1) > 0.3
            )
        )
        unique_queries = list(set(queries))[:5]

        return {
            "action": "research" if should_research else "revise",
            "should_research": should_research,
            "search_queries": unique_queries,
        }

    @staticmethod
    def _build_review_context(state: ResearchState) -> dict[str, Any]:
        """组装参考 CriticMaster 使用的审核上下文。"""

        draft_content = ""
        for section_id, content in state.draft_sections.items():
            section = next((item for item in state.outline if item.get("id") == section_id), {})
            draft_content += f"\n## {section.get('title', section_id)}\n{content}\n"
        if not draft_content:
            draft_content = state.final_report or "（暂无内容）"

        facts = "\n".join(
            f"- [{fact.get('id')}] {str(fact.get('content', ''))[:150]} "
            f"(来源: {fact.get('source_name') or fact.get('source_title')}, "
            f"可信度: {fact.get('credibility_score', fact.get('confidence'))})"
            for fact in state.facts[:20]
        ) or "（暂无事实记录）"
        data_points = "\n".join(
            f"- {point.get('name')}: {point.get('value')} {point.get('unit', '')} "
            f"(来源: {point.get('source')})"
            for point in state.data_points[:15]
        ) or "（暂无数据点）"
        outline = "\n".join(
            f"- {section.get('id')}: {section.get('title')} ({section.get('status', 'pending')})"
            for section in state.outline
        )
        # The structured aliases keep the existing MockLLM and telemetry contracts.
        # The real model receives the reference prompt rendered from the *_text values.
        return {
            "query": state.query,
            "outline": [
                {
                    "id": section.get("id", ""),
                    "title": section.get("title", ""),
                    "status": section.get("status", "pending"),
                }
                for section in state.outline
            ],
            "outline_text": outline,
            "draft_content": draft_content[:8000],
            "report": state.final_report[:8000],
            "facts": [
                {
                    "id": fact.get("id") or f"fact_{index}",
                    "content": str(fact.get("content", ""))[:150],
                    "source_name": fact.get("source_name") or fact.get("source_title", ""),
                    "source_url": fact.get("source_url", ""),
                    "credibility_score": fact.get(
                        "credibility_score", fact.get("confidence", 0.0)
                    ),
                }
                for index, fact in enumerate(state.facts[:20], start=1)
            ],
            "facts_text": facts,
            "sources": [
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source": source.get("source", ""),
                    "date": source.get("date", ""),
                }
                for source in state.raw_sources[:30]
            ],
            "data_points": state.data_points[:15],
            "data_points_text": data_points,
        }

    @staticmethod
    def _validate_review(value: Any, state: ResearchState | None = None) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Critic 返回结果必须是对象")

        assessment = value.get("overall_assessment", {})
        if not isinstance(assessment, dict):
            # Some compatible models flatten the assessment or return its
            # summary as a string. The reference Critic consumes missing
            # assessment fields with defaults instead of failing the run.
            assessment = {}

        verdict = CriticAgent._normalize_verdict(
            assessment.get("verdict", assessment.get("decision", value.get("verdict", "")))
        )
        if verdict is None:
            raw_verdict = assessment.get(
                "verdict", assessment.get("decision", value.get("verdict", ""))
            )
            if not str(raw_verdict or "").strip():
                # The reference consumer defaults a missing decision to the
                # revision path. Keep that safe fallback for omitted fields.
                verdict = "needs_revision"
            else:
                raise ValueError("Critic verdict 必须是 pass、needs_revision 或 major_issues")

        raw_score = assessment.get("quality_score", value.get("quality_score"))
        quality_score = CriticAgent._normalize_score(raw_score)
        if not 0 <= quality_score <= 10:
            raise ValueError("Critic quality_score 必须在 0 到 10 之间")

        issues = CriticAgent._validate_issues(
            value.get("issues", value.get("problems", []))
        )

        fact_checks = CriticAgent._as_list(value.get("fact_check_results", []))
        normalized_fact_checks = []
        for index, item in enumerate(fact_checks, start=1):
            if not isinstance(item, dict):
                continue
            fact_id = str(item.get("fact_id", item.get("id", ""))).strip()
            if not fact_id and state and index <= len(state.facts):
                fact_id = str(state.facts[index - 1].get("id") or f"fact_{index}")
            if not fact_id:
                # A fact-check record without an ID cannot be joined to a
                # fact. Drop that optional record rather than fail the review.
                continue
            status = CriticAgent._normalize_fact_status(item.get("status"))
            normalized_fact_checks.append(
                FactCheckResult(
                    fact_id=fact_id,
                    status=status,
                    reason=str(item.get("reason", item.get("explanation", ""))).strip(),
                ).to_dict()
            )

        missing_aspects = CriticAgent._validate_string_list(
            value.get("missing_aspects", []), "missing_aspects"
        )
        strengths = CriticAgent._validate_string_list(
            value.get("strength_points", value.get("strengths", [])), "strength_points"
        )

        search_queries = CriticAgent._validate_string_list(
            value.get("search_queries", []), "search_queries"
        )
        needs_more_research = CriticAgent._normalize_bool(
            value.get("needs_more_research"), default=bool(search_queries or missing_aspects)
        )

        assessment_summary = assessment.get("summary")
        if assessment_summary is None and isinstance(value.get("overall_assessment"), str):
            assessment_summary = value["overall_assessment"]
        summary = str(assessment_summary or value.get("summary", "")).strip()
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
        items = CriticAgent._as_list(value)
        normalized = []
        for item in items:
            if isinstance(item, str) and item.strip():
                normalized.append(item.strip())
            elif isinstance(item, dict):
                text = item.get("text", item.get("query", item.get("aspect", "")))
                if isinstance(text, str) and text.strip():
                    normalized.append(text.strip())
        return normalized

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        """Turn common singleton responses into a list without losing entries."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    @staticmethod
    def _normalize_verdict(value: Any) -> str | None:
        label = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "pass": "pass",
            "approved": "pass",
            "approve": "pass",
            "accepted": "pass",
            "通过": "pass",
            "可通过": "pass",
            "needs_revision": "needs_revision",
            "need_revision": "needs_revision",
            "revise": "needs_revision",
            "revision": "needs_revision",
            "needs_revise": "needs_revision",
            "需要修改": "needs_revision",
            "待修订": "needs_revision",
            "major_issues": "major_issues",
            "major_issue": "major_issues",
            "rejected": "major_issues",
            "reject": "major_issues",
            "严重问题": "major_issues",
        }
        return aliases.get(label)

    @staticmethod
    def _normalize_score(value: Any) -> float:
        """Accept numeric strings such as ``8分`` and ``8/10`` from LLMs."""
        if value is None or value == "":
            # CriticMaster's consumer reads quality_score with a 0.0 default.
            return 0.0
        if isinstance(value, bool):
            raise ValueError("Critic quality_score 必须是数字")
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"-?\d+(?:\.\d+)?", str(value))
        if not match:
            raise ValueError("Critic quality_score 必须是数字")
        try:
            return float(match.group())
        except ValueError as exc:
            raise ValueError("Critic quality_score 必须是数字") from exc

    @staticmethod
    def _normalize_fact_status(value: Any) -> str:
        status = str(value or "").strip().lower().replace(" ", "_")
        aliases = {
            "verified": "verified",
            "confirmed": "verified",
            "true": "verified",
            "已核实": "verified",
            "已验证": "verified",
            "unverified": "unverified",
            "not_verified": "unverified",
            "需要核实": "unverified",
            "待核实": "unverified",
            "suspicious": "suspicious",
            "疑似": "suspicious",
            "存疑": "suspicious",
            "false": "false",
            "incorrect": "false",
            "错误": "false",
        }
        return aliases.get(status, "unverified")

    @staticmethod
    def _normalize_bool(value: Any, *, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "1", "是", "需要", "需要搜索"}:
                return True
            if normalized in {"false", "no", "0", "否", "不需要", "无需搜索"}:
                return False
        return default

    @staticmethod
    def _validate_issues(value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []

        normalized = []
        for index, item in enumerate(CriticAgent._as_list(value), start=1):
            if isinstance(item, str):
                description = item.strip()
                if not description:
                    continue
                item = {
                    "id": f"issue_{index}",
                    "target_section": "global",
                    "issue_type": "incomplete",
                    "severity": "major",
                    "description": description,
                    "suggestion": description,
                }
            if not isinstance(item, dict):
                continue
            issue_id = str(item.get("id", f"issue_{index}")).strip() or f"issue_{index}"
            target_section = str(
                item.get("target_section", item.get("section_id", item.get("section", "global")))
            ).strip() or "global"
            if target_section in {"全局", "整体", "报告级"}:
                target_section = "global"
            issue_type = CriticAgent._normalize_issue_type(
                item.get("issue_type", item.get("type", "incomplete"))
            )
            severity = CriticAgent._normalize_severity(item.get("severity", "minor"))
            description = str(
                item.get("description", item.get("issue", item.get("problem", "")))
            ).strip()
            suggestion = str(
                item.get("suggestion", item.get("recommendation", item.get("fix", "")))
            ).strip()
            if not description and suggestion:
                description = suggestion
            if not description:
                continue
            if not suggestion:
                suggestion = description
            requires_new_search = CriticAgent._normalize_bool(
                item.get("requires_new_search"),
                default=False,
            )
            search_query = item.get("search_query", item.get("query", ""))
            if isinstance(search_query, list):
                search_query = next(
                    (query for query in search_query if isinstance(query, str) and query.strip()),
                    "",
                )
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
                    requires_new_search=requires_new_search,
                    search_query=str(search_query or "").strip(),
                    resolved=CriticAgent._normalize_bool(item.get("resolved")),
                ).to_dict()
            )
        return normalized

    @staticmethod
    def _normalize_issue_type(value: Any) -> str:
        issue_type = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "missing_source": "missing_source",
            "source_missing": "missing_source",
            "no_source": "missing_source",
            "缺少来源": "missing_source",
            "来源缺失": "missing_source",
            "logic_error": "logic_error",
            "logical_error": "logic_error",
            "逻辑错误": "logic_error",
            "bias": "bias",
            "偏见": "bias",
            "hallucination": "hallucination",
            "unsupported_claim": "hallucination",
            "幻觉": "hallucination",
            "outdated": "outdated",
            "out_of_date": "outdated",
            "过时": "outdated",
            "incomplete": "incomplete",
            "missing_aspect": "incomplete",
            "信息不完整": "incomplete",
            "遗漏": "incomplete",
        }
        return aliases.get(issue_type, issue_type if issue_type in {
            "missing_source", "logic_error", "bias", "hallucination", "outdated", "incomplete"
        } else "incomplete")

    @staticmethod
    def _normalize_severity(value: Any) -> str:
        severity = str(value or "").strip().lower()
        aliases = {
            "critical": "critical",
            "high": "critical",
            "严重": "critical",
            "致命": "critical",
            "major": "major",
            "medium": "major",
            "moderate": "major",
            "重要": "major",
            "中": "major",
            "minor": "minor",
            "low": "minor",
            "轻微": "minor",
            "低": "minor",
        }
        return aliases.get(severity, "minor")
