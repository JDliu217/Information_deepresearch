"""研究报告写作 Agent。"""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """按章节整理事实，并生成带来源的 Markdown 报告。"""

    name = "writer"
    MAX_REVISION_REPORT_CHARS = 24000
    MAX_REVISION_FACTS = 20
    SECTION_WRITING_SYSTEM = "你是资深研究分析师，擅长依据来源材料撰写清晰、严谨的研究报告。"
    SYNTHESIS_SYSTEM = "你是资深的研究报告主编，擅长整合和打磨最终报告。"
    REVISION_SYSTEM = "你是负责修订报告的资深编辑。"
    SECTION_WRITING_PROMPT = r"""你是一位资深研究分析师。请依据用户的问题和本章节材料写作，不预设研究领域，不引入与研究对象无关的主题。

## 研究主题
{query}

## 当前章节信息
标题: {section_title}
描述: {section_description}
类型: {section_type}

## 可用素材

### 相关事实
{facts}

### 可用来源链接
{sources}

### 数据点
{data_points}

### 已有洞察
{insights}

### 相关图表
{charts_info}

## 写作要求
1. **专业性**：使用与当前研究主题相符的术语，准确解释必要概念
2. **逻辑性**：论点清晰，论据充分，层层递进
3. **数据支撑**：关键观点必须有数据或事实支撑
4. **引用规范**：使用可点击链接格式 [来源名称](URL)，来源名称和 URL 必须来自可用素材
5. **图表整合**：在合适位置插入图表引用 ![图表标题](chart_id)
6. **字数控制**：本章节 500-1000 字
7. **不要重复标题**：正文开头不要再写章节标题

## 输出格式
```json
{{
    "content": "章节正文内容（Markdown格式，不包含章节标题）",
    "key_points": ["本章节的核心要点"],
    "citations": [
        {{"source": "来源名称", "url": "完整URL"}}
    ],
    "suggested_improvements": ["如果有更多信息可以改进的地方"]
}}
```

## 写作约束
- 开头直接回应本章节主题，不要使用与当前研究对象无关的行业或领域作为示例
- 只使用可用素材中的事实和数据；素材没有提供时明确说明，不得补造
- 需要引用时使用 [来源名称](URL) 格式，不得编造来源链接
- 站点首页或栏目页不能单独作为具体数字、公告或文章的证据；只有这类链接时，说明该项无法从现有来源核实

开始撰写："""
    SYNTHESIS_PROMPT = r"""你是首席笔杆，需要将各章节整合成完整的研究报告。

## 研究主题
{query}

## 各章节内容
{sections_content}

## 收集的所有引用来源
{all_sources}

## 任务
1. 撰写报告摘要（Executive Summary）
2. 整合各章节，确保逻辑连贯，使用层级编号
3. 撰写有证据支持的结论；只有主题适用时才提出展望，不要强行预测
4. 整理参考文献列表（确保链接可点击）
5. 只能引用“收集的所有引用来源”中逐字出现的 URL；没有对应来源时不得补造参考文献

## 关键要求

### 1. 标题编号规则（必须严格遵守）
- 一级标题：1、2、3...（如：1 [章节标题]）
- 二级标题：1.1、1.2、2.1...（如：1.1 [子章节标题]）
- 三级标题：1.1.1、1.1.2...（如：1.1.1 [更细分的标题]）
- **禁止标题重复**：每个标题必须唯一，不要在正文中重复章节标题

### 2. 引用格式规则（确保可点击）
- 行内引用：使用 [来源名称](URL) 格式，链接必须来自可用素材
- 数据引用：在数据后标注对应来源；没有来源支持的数据不得写入报告
- 若同一指标、期间和单位出现不同数值，保留差异并说明统计口径或来源不一致；证据不足时不得自行选值或计算折中值
- 文末参考文献：使用有序列表 + 可点击链接格式

### 3. 报告结构规范
- 不要在报告开头使用 # 一级标题
- 直接从"执行摘要"开始
- 各章节使用 ## 二级标题
- 子章节使用 ### 三级标题

## 输出格式
```json
{{
    "executive_summary": "执行摘要（300-500字）",
    "full_report": "完整报告（Markdown格式，按下方结构生成）",
    "conclusions": ["核心结论1", "核心结论2"],
    "outlook": "仅当研究主题适用时填写的展望；不适用时说明原因",
    "references": [
        {{"id": 1, "title": "来源标题", "url": "完整URL", "author": "作者/机构", "date": "日期"}}
    ]
}}
```

## 报告结构模板
```markdown
## 执行摘要

[300-500字的研究摘要]

---

## 1 [第一章标题]

[章节引言段落]

### 1.1 [子章节标题]

[内容，包含数据引用如：根据[来源名](URL)，...]

### 1.2 [子章节标题]

#### 1.2.1 [三级标题]

[更详细的内容]

---

## 2 [第二章标题]

### 2.1 [子章节标题]

...

---

## 结论

### 核心结论
1. [结论1]
2. [结论2]

### 后续值得关注的方向（仅在主题适用时）
[有来源支持的后续方向；不适用时省略本节]

---

## 参考文献

1. [来源标题1](URL1) - 作者/机构, 日期
2. [来源标题2](URL2) - 作者/机构, 日期
...
```"""
    REVISION_PROMPT = r"""你是首席笔杆，需要根据审核反馈修订报告。

## 原始报告
{original_content}

## 审核反馈
{feedback}

## 补充的新信息
{new_info}

## 任务
根据反馈修订报告，解决指出的问题。

## 修订原则
1. 针对性修改：只修改有问题的部分
2. 补充来源：对缺少来源的观点补充引用
3. 修正错误：纠正事实错误或逻辑漏洞
4. 保持风格：修订后保持报告整体风格一致
5. 每条反馈都带有稳定的问题 ID；`addressed_issues` 和 `unable_to_address` 必须使用这些原 ID。补充事实附有来源名称和 URL；引用时只能使用给出的 URL。没有证据支持的问题要明确说明无法核实，不得猜测或编造。
6. 保留原报告中未被指出的问题的章节和内容，不要因修订遗漏整章或截断结论、参考文献。

输出JSON：
```json
{{
    "revised_content": "修订后的内容",
    "changes_made": ["修改1", "修改2"],
    "addressed_issues": ["已解决的问题ID"],
    "unable_to_address": [{{"issue_id": "原问题ID", "reason": "无法解决的原因"}}]
}}
```"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(
        self,
        state: ResearchState,
        *,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> ResearchState:
        if not state.outline:
            raise ValueError("没有可用于写作的研究大纲")
        self._emit_progress(
            state,
            "research_step",
            {
                "step_type": "writing",
                "title": "内容生成",
                "subtitle": "撰写研究报告",
                "status": "running",
                "stats": {"sections_count": len(state.outline), "word_count": 0},
            },
            progress_callback,
        )
        draft_sections: dict[str, str] = dict(state.draft_sections)
        normalized_outline: list[dict] = []
        for index, raw_section in enumerate(state.outline, start=1):
            section = dict(raw_section)
            section_id = str(section.get("id", f"sec_{index}")).strip() or f"sec_{index}"
            section["id"] = section_id
            section_title = str(section.get("title", "")).strip() or f"第 {index} 节"
            section["title"] = section_title

            if section.get("status") in {"final", "drafted"}:
                normalized_outline.append(section)
                continue
            self._emit_progress(
                state,
                "action",
                {
                    "tool": "writing_section",
                    "section": section_title,
                    "section_id": section_id,
                },
                progress_callback,
            )
            related_facts = self._facts_for_section(state.facts, section_id)
            facts_text = "\n".join(
                f"- {fact.get('content')} (来源: [{fact.get('source_name') or fact.get('source_title') or '未知来源'}]"
                f"({fact.get('source_url') or '无可用URL'}), "
                f"可信度: {fact.get('credibility_score', fact.get('confidence'))})"
                for fact in related_facts
            ) or "（暂无相关事实）"
            sources_text = self._format_section_sources(related_facts)
            data_text = "\n".join(
                f"- {point.get('name')}: {point.get('value')} {point.get('unit', '')} "
                f"({point.get('year', 'N/A')}; 来源URL: {self._source_url_for_attribution(point.get('source'), state.facts)})"
                for point in state.data_points[:10]
            ) or "（暂无数据点）"
            insights_text = "\n".join(f"- {insight}" for insight in state.insights[:5]) or "（暂无洞察）"
            charts = [chart for chart in state.charts if chart.get("section_id") == section_id]
            charts_info = "\n".join(
                f"- 图表: {chart.get('title')} (ID: {chart.get('id')})" for chart in charts
            ) or "（暂无图表）"
            section_payload = {
                "mode": "section",
                "query": state.query,
                "section": section,
                "facts": related_facts,
                "data_points": state.data_points[:10],
                "insights": state.insights[:5],
                "charts": charts,
                "code_executions": state.code_executions,
                "review_result": state.review_result,
                "iteration": state.iteration,
                "instruction": "只生成本章节正文，不要重复章节标题；每个事实都保留可点击来源链接。",
            }
            section_response = await self._complete_text(
                section_payload,
                system_prompt=self.SECTION_WRITING_SYSTEM,
                user_prompt=self.SECTION_WRITING_PROMPT.format(
                    query=state.query,
                    section_title=section_title,
                    section_description=section.get("description", ""),
                    section_type=section.get("section_type", "mixed"),
                    facts=facts_text,
                    sources=sources_text,
                    data_points=data_text,
                    insights=insights_text,
                    charts_info=charts_info,
                ),
                json_mode=True,
                temperature=0.4,
                max_tokens=16000,
            )
            section_content, section_result = self._parse_writing_response(section_response, "content")
            if not section_content:
                normalized_outline.append(section)
                continue

            section_content, invalid_urls = self._remove_unverified_links(
                section_content, self._allowed_citation_urls(state)
            )
            if invalid_urls:
                state.logs.append(
                    {
                        "agent": self.name,
                        "event": "unsupported_citations_removed",
                        "section_id": section_id,
                        "urls": invalid_urls,
                    }
                )

            section["status"] = "drafted"
            draft_sections[section_id] = section_content
            rejected_citation_urls: list[str] = []
            for citation in section_result.get("citations", []):
                citation_url = str(citation.get("url", "")).strip()
                allowed_urls = {
                    self._canonical_url(url) for url in self._allowed_citation_urls(state)
                }
                if not citation_url or self._canonical_url(citation_url) not in allowed_urls:
                    if citation_url:
                        rejected_citation_urls.append(citation_url)
                    continue
                state.references.append(
                    {
                        "id": len(state.references) + 1,
                        "marker": citation.get("marker"),
                        "source": citation.get("source"),
                        "url": citation.get("url", ""),
                    }
                )
            if rejected_citation_urls:
                state.logs.append(
                    {
                        "agent": self.name,
                        "event": "unsupported_citations_removed",
                        "section_id": section_id,
                        "urls": list(dict.fromkeys(rejected_citation_urls)),
                    }
                )
            normalized_outline.append(section)
            self._emit_progress(
                state,
                "section_content",
                {
                    "section_id": section_id,
                    "section_title": section_title,
                    "content": section_content,
                    "word_count": len(section_content),
                    "key_points": section_result.get("key_points", []),
                },
                progress_callback,
            )

        sections_content = "\n\n".join(
            f"## {section.get('title')}\n{draft_sections[section['id']]}"
            for section in normalized_outline
            if draft_sections.get(section["id"])
        ) or "（暂无章节内容）"
        state.references = [
            reference
            for reference in state.references
            if isinstance(reference, dict)
            and self._is_allowed_citation_url(reference.get("url"), state)
        ]
        source_lines = [
            f"- {ref.get('source') or ref.get('title')} ({ref.get('url', 'N/A')})"
            for ref in state.references
            if self._is_allowed_citation_url(ref.get("url"), state)
        ]
        for fact in state.facts:
            source_line = (
                f"- {fact.get('source_name') or fact.get('source_title')} "
                f"({fact.get('source_url', 'N/A')})"
            )
            if source_line not in source_lines:
                source_lines.append(source_line)
        for source in state.raw_sources:
            url = str(source.get("url", "")).strip()
            if not url or not self._is_allowed_source_url(url, state):
                continue
            source_name = str(source.get("title") or source.get("source") or url).strip()
            scope = "（站点首页/栏目页，不能单独证明具体事实）" if self._is_landing_page(url) else ""
            source_line = f"- {source_name} ({url}) {scope}".strip()
            if source_line not in source_lines:
                source_lines.append(source_line)
        report_payload = {
            "mode": "report",
            "query": state.query,
            "outline": normalized_outline,
            "facts": state.facts[:30],
            "draft_sections": draft_sections,
            "data_points": state.data_points[:20],
            "insights": state.insights[:10],
            "charts": state.charts,
            "code_executions": state.code_executions,
            "references": state.references[:30],
            "review_result": state.review_result,
            "iteration": state.iteration,
            "instruction": "整合各章节草稿，生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
        }
        report_response = await self._complete_text(
            report_payload,
            system_prompt=self.SYNTHESIS_SYSTEM,
            user_prompt=self.SYNTHESIS_PROMPT.format(
                query=state.query,
                sections_content=sections_content,
                all_sources="\n".join(source_lines[:30]) or "（暂无来源）",
            ),
            json_mode=True,
            temperature=0.3,
            max_tokens=16000,
        )
        report, report_result = self._parse_writing_response(report_response, "full_report")
        has_synthesis_report = bool(report)
        executive_summary = report_result.get("executive_summary", "")
        conclusions = report_result.get("conclusions", [])
        if not report:
            report = f"# {state.query} 研究报告\n\n" + "\n\n".join(
                f"## {section.get('title', section['id'])}\n\n{draft_sections[section['id']]}"
                for section in normalized_outline
                if draft_sections.get(section["id"])
            )

        report, invalid_urls = self._remove_unverified_links(
            report, self._allowed_citation_urls(state)
        )
        if invalid_urls:
            state.logs.append(
                {
                    "agent": self.name,
                    "event": "unsupported_citations_removed",
                    "section_id": "report",
                    "urls": invalid_urls,
                }
            )

        state.outline = normalized_outline
        state.draft_sections = draft_sections
        state.final_report = report
        if has_synthesis_report:
            for reference in report_result.get("references", []):
                if (
                    isinstance(reference, dict)
                    and self._is_allowed_citation_url(reference.get("url"), state)
                    and reference not in state.references
                ):
                    state.references.append(reference)
        state.phase = "reviewing"
        self._emit_progress(
            state,
            "report_draft",
            {
                "content": state.final_report,
                "executive_summary": executive_summary,
                "conclusions": conclusions,
                "word_count": len(state.final_report),
                "references_count": len(state.references),
            },
            progress_callback,
        )
        self._emit_progress(
            state,
            "research_step",
            {
                "step_type": "writing",
                "title": "内容生成",
                "subtitle": "撰写研究报告",
                "status": "completed",
                "stats": {
                    "sections_count": len(state.outline),
                    "word_count": len(state.final_report),
                    "references_count": len(state.references),
                },
            },
            progress_callback,
        )
        return state

    async def revise(
        self,
        state: ResearchState,
        *,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> ResearchState:
        """审核后的报告修订模式，对齐 LeadWriter 的 revision 分支。"""

        if not state.final_report.strip():
            raise ValueError("没有可供修订的报告")
        self._emit_progress(
            state,
            "thought",
            {"content": "根据审核反馈修订报告..."},
            progress_callback,
        )
        unresolved = [
            issue
            for issue in state.critic_feedback
            if isinstance(issue, dict) and not issue.get("resolved")
        ]
        supplementary_facts = [
            fact
            for fact in state.facts
            if isinstance(fact.get("metadata"), dict)
            and fact["metadata"].get("analysis_mode") == "supplementary"
            and fact["metadata"].get("research_iteration") == state.iteration
        ]
        new_facts = (supplementary_facts or state.facts[-5:])[-self.MAX_REVISION_FACTS :]
        new_info = "\n".join(
            self._format_revision_fact(fact) for fact in new_facts
        ) or "无补充信息"
        original_content = state.final_report[: self.MAX_REVISION_REPORT_CHARS]
        payload = {
            "mode": "revision",
            "query": state.query,
            "original_content": original_content,
            "feedback": unresolved,
            "new_facts": new_facts,
            "iteration": state.iteration,
        }
        revised_response = await self._complete_text(
            payload,
            system_prompt=self.REVISION_SYSTEM,
            user_prompt=self.REVISION_PROMPT.format(
                original_content=original_content,
                feedback="\n".join(
                    f"- ID: {issue.get('id', 'unknown')} | [{issue.get('severity')}] "
                    f"{issue.get('issue_type', '未分类')} | 位置: {issue.get('location') or issue.get('target_section') or '未指定'}\n"
                    f"  问题: {issue.get('description')}\n"
                    f"  依据: {issue.get('evidence') or '审核未提供具体依据'}\n"
                    f"  建议: {issue.get('suggestion')}"
                    for issue in unresolved
                ) or "无具体反馈",
                new_info=new_info,
            ),
            json_mode=True,
            temperature=0.3,
            max_tokens=16000,
        )
        revised, revision_result = self._parse_writing_response(
            revised_response, "revised_content"
        )
        if revised:
            state.final_report = revised
            addressed = revision_result.get("addressed_issues", [])
            if isinstance(addressed, list):
                addressed_ids = {str(item).strip() for item in addressed}
                for issue in state.critic_feedback:
                    if issue.get("id") in addressed_ids:
                        # Writer's claim is recorded for the next independent
                        # Critic pass; only Critic may close an issue.
                        issue["writer_claimed_addressed"] = True
                        issue["writer_claimed_iteration"] = state.iteration
            unable_to_address = revision_result.get("unable_to_address", [])
            if isinstance(unable_to_address, list):
                for item in unable_to_address:
                    if not isinstance(item, dict):
                        continue
                    issue_id = str(item.get("issue_id", "")).strip()
                    reason = str(item.get("reason", "")).strip()
                    for issue in state.critic_feedback:
                        if issue.get("id") == issue_id:
                            issue["writer_unable_reason"] = reason
                            issue["writer_claimed_iteration"] = state.iteration
        state.phase = "reviewing"
        self._emit_progress(
            state,
            "report_draft",
            {
                "content": state.final_report,
                "word_count": len(state.final_report),
                "revision": True,
            },
            progress_callback,
        )
        return state

    @staticmethod
    def _format_revision_fact(fact: dict[str, Any]) -> str:
        """Include source attribution so a revision can cite new evidence."""

        content = str(fact.get("content", "")).strip()[:600]
        source_name = str(fact.get("source_name") or fact.get("source_title") or "").strip()
        source_url = str(fact.get("source_url", "")).strip()
        metadata = fact.get("metadata") if isinstance(fact.get("metadata"), dict) else {}
        search_query = str(metadata.get("search_query", "")).strip()
        attribution = f"来源：[{source_name or '来源'}]({source_url})" if source_url else "来源链接缺失"
        query_context = f"；补充查询：{search_query}" if search_query else ""
        return f"- {content}\n  {attribution}{query_context}"

    @staticmethod
    def _format_section_sources(facts: list[dict[str, Any]]) -> str:
        """Give the model exact retrieved URLs and flag generic landing pages."""

        lines: list[str] = []
        seen: set[str] = set()
        for fact in facts:
            url = str(fact.get("source_url", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            title = str(
                fact.get("source_name") or fact.get("source_title") or "未知来源"
            ).strip()
            scope = (
                "站点首页/栏目页，不能单独作为具体事实证据"
                if WriterAgent._is_landing_page(url)
                else "搜索结果详情链接"
            )
            lines.append(f"- {title} | {url} | {scope}")
        return "\n".join(lines) or "（没有带有效 URL 的章节来源；不要生成引用链接）"

    @staticmethod
    def _allowed_source_urls(state: ResearchState) -> set[str]:
        urls = {
            str(source.get("url", "")).strip()
            for source in state.raw_sources
            if isinstance(source, dict) and str(source.get("url", "")).strip()
        }
        urls.update(
            str(fact.get("source_url", "")).strip()
            for fact in state.facts
            if isinstance(fact, dict) and str(fact.get("source_url", "")).strip()
        )
        return urls

    @staticmethod
    def _allowed_citation_urls(state: ResearchState) -> set[str]:
        """A retrieved homepage is not citable evidence for a concrete claim."""

        return {
            url
            for url in WriterAgent._allowed_source_urls(state)
            if not WriterAgent._is_landing_page(url)
        }

    @staticmethod
    def _canonical_url(value: str) -> str:
        parsed = urlparse(value.strip())
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            return ""
        return parsed._replace(
            scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower()
        ).geturl().rstrip("/")

    @staticmethod
    def _is_allowed_source_url(value: Any, state: ResearchState) -> bool:
        url = str(value or "").strip()
        if not url:
            return False
        canonical = WriterAgent._canonical_url(url)
        return bool(canonical) and canonical in {
            WriterAgent._canonical_url(candidate)
            for candidate in WriterAgent._allowed_source_urls(state)
        }

    @staticmethod
    def _is_allowed_citation_url(value: Any, state: ResearchState) -> bool:
        url = str(value or "").strip()
        if not url or WriterAgent._is_landing_page(url):
            return False
        canonical = WriterAgent._canonical_url(url)
        return bool(canonical) and canonical in {
            WriterAgent._canonical_url(candidate)
            for candidate in WriterAgent._allowed_citation_urls(state)
        }

    @staticmethod
    def _remove_unverified_links(
        content: str, allowed_urls: set[str]
    ) -> tuple[str, list[str]]:
        allowed = {WriterAgent._canonical_url(url) for url in allowed_urls}
        invalid: list[str] = []

        def replace(match: re.Match[str]) -> str:
            label, url = match.group(1), match.group(2).strip()
            if WriterAgent._canonical_url(url) in allowed:
                return match.group(0)
            invalid.append(url)
            if WriterAgent._is_landing_page(url):
                return f"{label}（站点首页/栏目页不能核验具体事实）"
            return f"{label}（来源链接未核验）"

        cleaned = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", replace, content)
        return cleaned, list(dict.fromkeys(invalid))

    @staticmethod
    def _is_landing_page(value: str) -> bool:
        parsed = urlparse(str(value or "").strip())
        path = parsed.path.strip("/").lower()
        return path in {
            "",
            "index",
            "index.html",
            "index.htm",
            "home",
            "homepage",
            "about",
            "news",
            "articles",
        }

    @staticmethod
    def _source_url_for_attribution(source: Any, facts: list[dict[str, Any]]) -> str:
        label = str(source or "").strip()
        for fact in facts:
            candidates = {
                str(fact.get("source_name", "")).strip(),
                str(fact.get("source_title", "")).strip(),
                str(fact.get("source_url", "")).strip(),
            }
            if label and label in candidates:
                return str(fact.get("source_url", "")).strip() or "无可用URL"
        return "无可用URL"

    def _emit_progress(
        self,
        state: ResearchState,
        event_type: str,
        content: dict[str, Any],
        callback: Callable[[dict[str, Any]], None] | None,
    ) -> None:
        """记录参考 LeadWriter 的增量消息，并交给 LangGraph custom stream。"""

        message = {
            "type": event_type,
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content,
        }
        state.messages.append(message)
        if callback is not None:
            callback(message)

    @staticmethod
    def _parse_writing_response(response: str, field: str) -> tuple[str, dict]:
        """Read a structured response like LeadWriter.parse_json_response.

        Plain prose is not accepted as a successful response. The reference
        Writer requests JSON and stores content only when the parsed object
        contains the expected field.
        """

        parsed = WriterAgent._parse_json_response(response)
        if not parsed:
            return "", {}
        content = parsed.get(field)
        return content if isinstance(content, str) else "", parsed

    @staticmethod
    def _parse_json_response(response: str) -> dict:
        """Parse model JSON, including the recovery steps used by BaseAgent."""

        if not isinstance(response, str):
            return {}

        def fix_escaped_values(value: Any, key: str | None = None) -> Any:
            if isinstance(value, dict):
                return {name: fix_escaped_values(item, name) for name, item in value.items()}
            if isinstance(value, list):
                return [fix_escaped_values(item, key) for item in value]
            if not isinstance(value, str) or key in {"code", "fixed_code", "revised_content"}:
                return value
            return (
                value.replace("\\\\n", "\n")
                .replace("\\n", "\n")
                .replace("\\\\r", "\r")
                .replace("\\r", "\r")
                .replace("\\\\t", "\t")
                .replace("\\t", "\t")
            )

        def try_parse(candidate: str) -> dict:
            candidate = candidate.strip()
            if candidate.startswith("\ufeff"):
                candidate = candidate[1:]
            try:
                result = json.loads(candidate)
                return fix_escaped_values(result) if isinstance(result, dict) else {}
            except json.JSONDecodeError:
                pass

            # These repair steps mirror BaseAgent.parse_json_response in the
            # reference project for common JSON formatting mistakes.
            repaired = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', "", candidate)
            repaired = re.sub(r"//.*?$", "", repaired, flags=re.MULTILINE)
            repaired = re.sub(r"/\*.*?\*/", "", repaired, flags=re.DOTALL)
            repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)
            repaired = re.sub(r'([}\]])(\s*)([{\[])', r"\1,\2\3", repaired)
            repaired = re.sub(r"(\{|,)\s*(\w+)\s*:", r'\1"\2":', repaired)
            try:
                result = json.loads(repaired)
                return fix_escaped_values(result) if isinstance(result, dict) else {}
            except json.JSONDecodeError:
                pass

            # Keep the reference parser's Python-literal fallback for outputs
            # that look like a dict but use single quotes/JSON booleans.
            python_candidate = re.sub(r"\btrue\b", "True", candidate)
            python_candidate = re.sub(r"\bfalse\b", "False", python_candidate)
            python_candidate = re.sub(r"\bnull\b", "None", python_candidate)
            try:
                literal = ast.literal_eval(python_candidate)
                return literal if isinstance(literal, dict) else {}
            except (SyntaxError, ValueError):
                return {}

        parsed = try_parse(response)
        if parsed:
            return parsed

        code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response, re.IGNORECASE)
        if code_block:
            parsed = try_parse(code_block.group(1))
            if parsed:
                return parsed

        start, end = response.find("{"), response.rfind("}")
        if start >= 0 and end > start:
            parsed = try_parse(response[start : end + 1])
            if parsed:
                return parsed
        return {}

    @staticmethod
    def _facts_for_section(
        facts: list[dict],
        section_id: str,
    ) -> list[dict]:
        """优先选择当前章节的事实；没有关联时回退到全部事实。"""
        related = [
            fact for fact in facts
            if section_id in (fact.get("related_sections") or [])
            or str(fact.get("section_id", "")).strip() == section_id
        ]
        return related or facts[:10]
