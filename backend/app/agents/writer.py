"""研究报告写作 Agent。"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """按章节整理事实，并生成带来源的 Markdown 报告。"""

    name = "writer"
    SECTION_WRITING_SYSTEM = "你是顶级的行业研究分析师，擅长撰写专业的研究报告。"
    SYNTHESIS_SYSTEM = "你是资深的研究报告主编，擅长整合和打磨最终报告。"
    REVISION_SYSTEM = "你是负责修订报告的资深编辑。"
    SECTION_WRITING_PROMPT = r"""你是一位顶级投行研究部的首席分析师，擅长撰写深度行业研究报告。

## 研究主题
{query}

## 当前章节信息
标题: {section_title}
描述: {section_description}
类型: {section_type}

## 可用素材

### 相关事实
{facts}

### 数据点
{data_points}

### 已有洞察
{insights}

### 相关图表
{charts_info}

## 写作要求
1. **专业性**：使用行业术语，体现专业深度
2. **逻辑性**：论点清晰，论据充分，层层递进
3. **数据支撑**：关键观点必须有数据或事实支撑
4. **引用规范**：使用可点击链接格式 [来源名称](URL)，如 [艾瑞咨询](https://www.iresearch.cn)
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

## 写作风格示例
- 好的开头："2024年，中国AI芯片市场正经历深刻变革。根据[IDC数据](https://www.idc.com)，市场规模达到..."
- 避免的开头："关于AI芯片，首先我们来看..."
- 数据引用示例："市场规模达5000亿元（[艾瑞咨询报告](https://www.iresearch.cn/report)）"

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
3. 撰写结论与展望
4. 整理参考文献列表（确保链接可点击）

## 关键要求

### 1. 标题编号规则（必须严格遵守）
- 一级标题：1、2、3...（如：1 市场概况）
- 二级标题：1.1、1.2、2.1...（如：1.1 市场规模）
- 三级标题：1.1.1、1.1.2...（如：1.1.1 全球市场）
- **禁止标题重复**：每个标题必须唯一，不要在正文中重复章节标题

### 2. 引用格式规则（确保可点击）
- 行内引用：使用 [来源名称](URL) 格式，如 [艾瑞咨询](https://www.iresearch.cn)
- 数据引用：在数据后标注来源，如"市场规模达5000亿元（[IDC报告](https://www.idc.com)）"
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
    "outlook": "未来展望",
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

## 结论与展望

### 核心结论
1. [结论1]
2. [结论2]

### 未来展望
[展望内容]

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

输出JSON：
```json
{{
    "revised_content": "修订后的内容",
    "changes_made": ["修改1", "修改2"],
    "addressed_issues": ["已解决的问题ID"],
    "unable_to_address": ["无法解决的问题及原因"]
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
                f"- {fact.get('content')} (来源: {fact.get('source_name') or fact.get('source_title')}, "
                f"可信度: {fact.get('credibility_score', fact.get('confidence'))})"
                for fact in related_facts
            ) or "（暂无相关事实）"
            data_text = "\n".join(
                f"- {point.get('name')}: {point.get('value')} {point.get('unit', '')} "
                f"({point.get('year', 'N/A')})"
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

            section["status"] = "drafted"
            draft_sections[section_id] = section_content
            self._merge_report_references(state, section_result.get("citations", []))
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
        source_lines = [
            f"- {ref.get('source') or ref.get('title')} ({ref.get('url', 'N/A')})"
            for ref in state.references
        ]
        for fact in state.facts:
            source_line = (
                f"- {fact.get('source_name') or fact.get('source_title')} "
                f"({fact.get('source_url', 'N/A')})"
            )
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
        if not report:
            report = f"# {state.query} 研究报告\n\n" + "\n\n".join(
                f"## {section.get('title', section['id'])}\n\n{draft_sections[section['id']]}"
                for section in normalized_outline
                if draft_sections.get(section["id"])
            )

        state.outline = normalized_outline
        state.draft_sections = draft_sections
        state.final_report = report
        self._merge_report_references(state, report_result.get("references", []))
        state.phase = "reviewing"
        self._emit_progress(
            state,
            "report_content",
            {
                "content": state.final_report,
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
        payload = {
            "mode": "revision",
            "query": state.query,
            "original_content": state.final_report[:6000],
            "feedback": unresolved,
            "new_facts": state.facts[-5:],
            "iteration": state.iteration,
        }
        revised_response = await self._complete_text(
            payload,
            system_prompt=self.REVISION_SYSTEM,
            user_prompt=self.REVISION_PROMPT.format(
                original_content=state.final_report[:6000],
                feedback="\n".join(
                    f"- [{issue.get('severity')}] {issue.get('description')}\n"
                    f"  建议: {issue.get('suggestion')}"
                    for issue in unresolved
                ) or "无具体反馈",
                new_info="\n".join(
                    f"- {str(fact.get('content', ''))[:200]}" for fact in state.facts[-5:]
                ) or "无补充信息",
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
                        issue["resolved"] = True
        state.phase = "reviewing"
        self._emit_progress(
            state,
            "report_content",
            {
                "content": state.final_report,
                "word_count": len(state.final_report),
                "revision": True,
            },
            progress_callback,
        )
        return state

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
        """Interpret structured Writer output; local mock text remains accepted."""

        raw = response.strip()
        match = re.fullmatch(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
        candidate = match.group(1) if match else raw
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return ("", {}) if candidate.lstrip().startswith(("{", "[")) else (raw, {})
        if not isinstance(parsed, dict):
            return "", {}
        content = parsed.get(field)
        return content.strip() if isinstance(content, str) else "", parsed

    @staticmethod
    def _merge_report_references(state: ResearchState, references: object) -> None:
        if not isinstance(references, list):
            return
        known_urls = {str(item.get("url", "")).strip() for item in state.references}
        allowed_urls = {str(item.get("url", "")).strip() for item in state.raw_sources}
        allowed_urls.update(str(item.get("source_url", "")).strip() for item in state.facts)
        for reference in references:
            if not isinstance(reference, dict):
                continue
            url = str(reference.get("url", "")).strip()
            if not url or url not in allowed_urls or url in known_urls:
                continue
            state.references.append({
                "id": len(state.references) + 1,
                "marker": reference.get("marker"),
                "source": reference.get("source") or reference.get("title", ""),
                "title": reference.get("title") or reference.get("source", ""),
                "url": url,
                "author": reference.get("author", ""),
                "date": reference.get("date", ""),
            })
            known_urls.add(url)

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
