"""统一的大模型客户端接口。

Agent 只依赖这里定义的接口，不直接依赖某一家模型服务的 SDK。
当前先实现 MockLLMClient，后续再实现真实的 OpenAI 兼容客户端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from typing import Any


class LLMClient(ABC):
    """所有 LLM 客户端都必须提供的能力。"""

    @abstractmethod
    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """让模型返回结构化 JSON 数据。"""
        raise NotImplementedError

    @abstractmethod
    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        """让模型返回普通文本。"""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """不联网的确定性客户端。

    Mock 的作用是先验证业务流程和状态流转，而不是模拟真正的智能程度。
    同样的输入会得到同样的输出，测试因此稳定且容易理解。
    """

    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if role == "planner":
            query = str(payload.get("query", "")).strip()
            if not query:
                raise ValueError("planner 请求缺少 query")

            return {
                "outline": [
                    {
                        "title": "现状与定义",
                        "description": f"明确“{query}”的研究范围和当前现状。",
                        "search_queries": [f"{query} 的当前现状和关键定义"],
                    },
                    {
                        "title": "问题与证据",
                        "description": "整理公开来源中的事实、数据和主要争议。",
                        "search_queries": [f"{query} 的主要问题和公开证据"],
                    },
                    {
                        "title": "趋势与建议",
                        "description": "根据已有证据判断未来趋势并提出建议。",
                        "search_queries": [f"{query} 的未来趋势和改进建议"],
                    },
                ],
                "research_questions": [
                    f"{query} 的当前现状和关键定义是什么？",
                    f"{query} 面临哪些主要问题，有哪些公开证据？",
                    f"{query} 的未来趋势和改进建议是什么？",
                ],
                "hypotheses": [
                    {
                        "id": "h_1",
                        "content": f"{query} 的发展趋势会受到政策和市场需求共同影响。",
                        "status": "unverified",
                    }
                ],
                "key_entities": [],
            }

        if role == "fact_extractor":
            facts = []
            hypotheses = payload.get("hypotheses", [])
            hypothesis = hypotheses[0] if hypotheses else None
            for index, source in enumerate(payload.get("sources", []), start=1):
                content = str(source.get("content") or source.get("snippet") or "").strip()
                url = str(source.get("url", "")).strip()
                if not content or not url:
                    continue
                fact = {
                    "content": content,
                    "source_title": str(source.get("title", "")).strip(),
                    "source_url": url,
                    "source_type": "web",
                    "confidence": 0.7,
                    "data_points": [
                        {
                            "name": "模拟来源指标",
                            "value": index * 10,
                            "unit": "单位",
                            "year": 2024,
                            "source": str(source.get("title", "")).strip() or url,
                            "confidence": 0.7,
                        }
                    ],
                }
                if hypothesis and hypothesis.get("id"):
                    fact["related_hypothesis"] = str(hypothesis["id"])
                    fact["hypothesis_support"] = "supports"
                facts.append(fact)
            query = str(payload.get("query", "")).strip() or "研究对象"
            return {
                "facts": facts,
                "extracted_facts": [
                    {
                        **fact,
                        "source_name": fact["source_title"],
                        "credibility_score": fact["confidence"],
                    }
                    for fact in facts
                ],
                "entities_discovered": [
                    {
                        "name": query,
                        "type": "industry",
                        "relations": ["受政策环境影响", "受市场需求影响"],
                    },
                    {"name": "政策环境", "type": "policy", "relations": []},
                    {"name": "市场需求", "type": "market", "relations": []},
                ],
                "key_insights": [],
                "follow_up_queries": [],
                "source_tracing_queries": [],
                "missing_info": [],
                "source_quality_assessment": "Mock 搜索结果仅用于测试数据流。",
            }

        if role == "data_analyst":
            mode = payload.get("mode")
            if mode == "data_extraction":
                # These explicitly synthetic values exercise the three-stage
                # contract without pretending the mock has inferred real facts.
                results = str(payload.get("search_results", ""))
                fact_count = sum(1 for line in results.splitlines() if line.strip().startswith("- "))
                if not fact_count:
                    return {"data_points": [], "time_series": [], "distributions": [], "insights": []}
                return {
                    "data_points": [{
                        "id": "dp_mock_fact_count",
                        "name": "Mock 流程事实条数",
                        "value": fact_count,
                        "unit": "条",
                        "year": 2024,
                        "source": "Mock 测试数据",
                        "category": "pipeline_check",
                        "confidence": 0.5,
                    }],
                    "time_series": [],
                    "distributions": [],
                    "insights": [f"Mock 数据流已收到 {fact_count} 条事实材料。"],
                }
            if mode == "knowledge_graph":
                return {"nodes": [], "edges": []}
            if mode == "chart_generation":
                chart_data = payload.get("data", {})
                if not isinstance(chart_data, dict):
                    return {"charts": []}
                data_points = chart_data.get("data_points", [])
                if not data_points:
                    return {"charts": []}
                categories = [str(point.get("name", "指标")) for point in data_points]
                values = [point.get("value") for point in data_points]
                return {
                    "charts": [{
                        "id": "chart_mock_data_points",
                        "title": f"{payload.get('query', '研究对象')} Mock 数据示例",
                        "type": "bar",
                        "echarts_option": {
                            "tooltip": {"trigger": "axis"},
                            "xAxis": {"type": "category", "data": categories},
                            "yAxis": {"type": "value"},
                            "series": [{"name": "Mock 示例数据", "type": "bar", "data": values}],
                        },
                    }]
                }
            raise ValueError(f"Mock DataAnalyst 不支持模式: {mode}")

        if role == "code_wizard":
            if payload.get("mode") == "repair":
                return {
                    "fixed_code": "result = {'data_point_count': len(data_points)}\nprint(result)",
                    "error_analysis": "修复执行错误。",
                    "fix_description": "改为统计可用数据点数量。",
                }
            if payload.get("mode") == "chart_generation":
                return {
                    "code": (
                        "plt.plot([2022, 2023, 2024], [10, 20, 30], marker='o')\n"
                        "plt.title('Mock 章节趋势')\n"
                        "plt.savefig('chart.png')"
                    ),
                    "chart_description": "Mock 章节趋势图；执行器当前不渲染图片。",
                }
            return {
                "analysis_plan": "统计已验证数据点的数量。",
                "code": (
                    "# CodeWizard 生成的待执行分析代码\n"
                    "data_point_count = len(data_points)\n"
                    "result = {'data_point_count': data_point_count}\n"
                    "print(result)"
                ),
                "expected_outputs": ["analysis_summary"],
            }

        if role == "critic":
            report = str(payload.get("report", "")).strip()
            facts = payload.get("facts", [])
            sources = payload.get("sources", [])
            if not report:
                raise ValueError("critic 请求缺少 report")

            passed = bool(facts and sources and "http" in report)
            return {
                "overall_assessment": {
                    "verdict": "pass" if passed else "needs_revision",
                    "quality_score": 8.0 if passed else 4.0,
                    "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
                },
                "verdict": "pass" if passed else "needs_revision",
                "quality_score": 8.0 if passed else 4.0,
                "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
                "needs_more_research": not passed,
                "issues": [] if passed else [{
                    "id": "issue_1",
                    "target_section": "global",
                    "issue_type": "missing_source",
                    "severity": "major",
                    "location": "报告正文",
                    "description": "需要补充带来源的事实",
                    "evidence": "报告没有足够的来源链接",
                    "suggestion": "补充权威来源并在正文中引用",
                    "requires_new_search": True,
                    "search_query": "补充权威来源和数据",
                }],
                "search_queries": [] if passed else ["补充权威来源和数据"],
                "fact_check_results": [
                    {
                        "fact_id": str(fact.get("id", f"fact_{index}")),
                        "status": "verified" if passed else "unverified",
                        "reason": "事实关联了来源" if passed else "需要进一步核查来源",
                    }
                    for index, fact in enumerate(facts, start=1)
                ],
                "missing_aspects": [] if passed else ["权威数据来源"],
                "strengths": ["报告包含研究问题和引用"] if passed else [],
            }

        raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        if role != "writer":
            raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")

        query = str(payload.get("query", "")).strip()
        if not query:
            raise ValueError("writer 请求缺少 query")

        if payload.get("mode") == "section":
            section = payload.get("section", {})
            title = str(section.get("title", "本章节")).strip() or "本章节"
            facts = payload.get("facts", [])
            lines = [f"本章节围绕“{title}”整理研究证据。"]
            for fact in facts:
                content = str(fact.get("content", "")).strip()
                if not content:
                    continue
                source_title = str(fact.get("source_title", "来源")).strip() or "来源"
                source_url = str(fact.get("source_url", "")).strip()
                citation = f" ([{source_title}]({source_url}))" if source_url else ""
                lines.append(f"- {content}{citation}")
            if len(lines) == 1:
                lines.append("当前章节还没有可引用的事实。")
            content = "\n".join(lines)
            if json_mode:
                return json.dumps(
                    {"content": content, "key_points": [], "citations": []},
                    ensure_ascii=False,
                )
            return content

        if payload.get("mode") == "revision":
            original = str(payload.get("original_content", "")).strip()
            issues = payload.get("feedback", [])
            lines = [original, "", "## 根据审核意见修订", ""]
            if issues:
                lines.extend(
                    f"- 已处理：{issue.get('description', issue) if isinstance(issue, dict) else issue}"
                    for issue in issues
                )
            else:
                lines.append("- 当前没有未解决的审核问题。")
            for fact in payload.get("new_facts", []):
                content = str(fact.get("content", "")).strip()
                source_url = str(fact.get("source_url", "")).strip()
                if content and source_url and content not in original:
                    lines.append(f"- {content} ([来源]({source_url}))")
            content = "\n".join(lines).strip()
            if json_mode:
                return json.dumps(
                    {
                        "revised_content": content,
                        "changes_made": [],
                        "addressed_issues": [],
                        "unable_to_address": [],
                    },
                    ensure_ascii=False,
                )
            return content

        if payload.get("mode") == "report":
            outline = payload.get("outline", [])
            draft_sections = payload.get("draft_sections", {})
            lines = [
                "## 执行摘要",
                "",
                f"本报告围绕“{query}”整理公开资料，并按研究大纲组织可验证证据。",
                "",
                "## 研究发现",
                "",
            ]
            for index, section in enumerate(outline, start=1):
                section_id = str(section.get("id", f"sec_{index}")).strip()
                title = str(section.get("title", f"第 {index} 节")).strip()
                content = str(draft_sections.get(section_id, "")).strip()
                if content:
                    lines.extend([f"### {index}. {title}", "", content, ""])

            insights = payload.get("insights", [])
            if insights:
                lines.extend(["## 数据洞察", ""])
                lines.extend(f"- {insight}" for insight in insights)
                lines.append("")

            charts = payload.get("charts", [])
            if charts:
                lines.extend(["## 图表", ""])
                for chart in charts:
                    title = str(chart.get("title", "未命名图表")).strip() or "未命名图表"
                    chart_type = str(
                        chart.get("chart_type", chart.get("type", "unknown"))
                    ).strip()
                    lines.append(f"- {title}（{chart_type}）")
                lines.append("")

            successful_executions = [
                item
                for item in payload.get("code_executions", [])
                if item.get("status") == "succeeded"
            ]
            if successful_executions:
                lines.extend(["## 代码分析", ""])
                for execution in successful_executions:
                    output = execution.get("result", {}).get("output", {})
                    lines.append(f"- {execution['id']}：{output}")
                lines.append("")

            review = payload.get("review_result", {})
            issues = review.get("issues", []) if isinstance(review, dict) else []
            if issues:
                lines.extend(["## 根据审核意见修订", ""])
                lines.extend(f"- 已处理：{issue}" for issue in issues)
                lines.append("")

            lines.extend(
                [
                    "## 结论",
                    "",
                    "以上结论需要结合更多官方统计和行业报告继续验证。",
                ]
            )
            content = "\n".join(lines)
            if json_mode:
                return json.dumps(
                    {
                        "full_report": content,
                        "executive_summary": "",
                        "conclusions": [],
                        "references": [],
                    },
                    ensure_ascii=False,
                )
            return content

        facts = payload.get("facts", [])
        lines = [
            "## 执行摘要",
            "",
            f"本报告围绕“{query}”整理公开资料，并只使用已收集的来源作为证据。",
            "",
            "## 研究发现",
            "",
        ]
        if facts:
            for index, fact in enumerate(facts, start=1):
                content = str(fact.get("content", "")).strip()
                title = str(fact.get("source_title", "来源")).strip() or "来源"
                url = str(fact.get("source_url", "")).strip()
                lines.append(f"{index}. {content} ([{title}]({url}))")
        else:
            lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")

        review = payload.get("review_result", {})
        issues = review.get("issues", []) if isinstance(review, dict) else []
        if issues:
            lines.extend(["", "## 根据审核意见修订", ""])
            lines.extend(f"- 已处理：{issue}" for issue in issues)

        lines.extend(
            [
                "",
                "## 结论",
                "",
                "以上结论需要结合更多官方统计和行业报告继续验证。",
            ]
        )
        content = "\n".join(lines)
        if json_mode:
            return json.dumps(
                {
                    "full_report": content,
                    "executive_summary": "",
                    "conclusions": [],
                    "references": [],
                },
                ensure_ascii=False,
            )
        return content
