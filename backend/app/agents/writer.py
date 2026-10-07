"""研究报告写作 Agent。"""

from __future__ import annotations

import json
import re

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """按章节整理事实，并生成带来源的 Markdown 报告。"""

    name = "writer"
    SECTION_WRITING_SYSTEM = """你是 DeepResearch 的专业行业研究写作 Agent。只能使用输入事实、数据、洞察
和来源；不能补写没有证据的数字或 URL。章节正文要区分事实、分析和判断，关键事实保留可点击来源。"""
    SECTION_WRITING_PROMPT = """请完成一个研究章节的写作任务。只生成章节正文，不重复章节标题；每个关键
事实保留输入中的来源链接，图表引用已有图表 ID。正文约 500 到 1000 字；资料不足时说明缺口，
不得补写输入没有的数字或来源。返回 JSON：
{"content":"Markdown 章节正文","key_points":["关键要点"],
 "citations":[{"source":"来源名称","url":"输入中的 URL"}],
 "suggested_improvements":["仍需补充的信息"]}。"""
    SYNTHESIS_PROMPT = """请整合全部章节草稿为完整研究报告，包含执行摘要、研究发现、数据洞察（若有）、
结论、展望和参考文献。保持逻辑连贯、引用可追溯，结论强度不能超过证据。
返回 JSON：{"executive_summary":"执行摘要","full_report":"完整 Markdown 报告",
"conclusions":["结论"],"outlook":"展望",
"references":[{"title":"来源标题","url":"输入中的 URL","author":"作者或机构","date":"日期"}]}。
完整报告必须包含各章节实质内容，关键事实与数字后有可点击来源链接，不能把未验证假设写成事实。"""
    REVISION_PROMPT = """请根据审核问题修订当前报告。只处理输入中列出的审核问题，保留正确事实和来源，
并说明已处理及无法处理的问题。新事实仅来自最近 5 条输入证据，引用它们时保留原 URL。
返回 JSON：{"revised_content":"修订后的完整 Markdown 报告",
"addressed_issues":["已处理的问题 ID"],"unable_to_address":["无法处理的问题 ID"],
"changes_made":["修改说明"]}。"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.outline:
            raise ValueError("没有可用于写作的研究大纲")
        if not state.facts:
            raise ValueError("没有可用于写作的事实")

        draft_sections: dict[str, str] = {}
        normalized_outline: list[dict] = []
        outline_ids = {
            str(section.get("id", "")).strip()
            for section in state.outline
            if str(section.get("id", "")).strip()
        }
        unassigned_facts = [
            fact
            for fact in state.facts
            if str(fact.get("section_id", "")).strip() not in outline_ids
        ]
        for index, raw_section in enumerate(state.outline, start=1):
            section = dict(raw_section)
            section_id = str(section.get("id", f"sec_{index}")).strip() or f"sec_{index}"
            section["id"] = section_id
            section_title = str(section.get("title", "")).strip() or f"第 {index} 节"
            section["title"] = section_title

            related_facts = self._facts_for_section(state.facts, section_id)
            if index == 1 and unassigned_facts:
                related_facts = self._merge_facts(related_facts, unassigned_facts)
            section_payload = {
                "mode": "section",
                "query": state.query,
                "section": section,
                "facts": related_facts[:10],
                "data_points": state.data_points[:10],
                "insights": state.insights[:5],
                "charts": self._charts_for_section(state.charts, section_id),
                "code_executions": state.code_executions,
                "review_result": state.review_result,
                "iteration": state.iteration,
                "instruction": "只生成本章节正文，不要重复章节标题；每个事实都保留可点击来源链接。",
            }
            section_response = await self._complete_text(
                section_payload,
                system_prompt=self.SECTION_WRITING_SYSTEM,
                user_prompt=self._render_prompt(self.SECTION_WRITING_PROMPT, section_payload),
            )
            section_content, _ = self._parse_writing_response(section_response, "content")
            if not section_content:
                raise ValueError(f"Writer 没有生成章节内容: {section_title}")

            section["status"] = "drafted"
            draft_sections[section_id] = section_content
            normalized_outline.append(section)

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
            system_prompt=self.SECTION_WRITING_SYSTEM,
            user_prompt=self._render_prompt(self.SYNTHESIS_PROMPT, report_payload),
        )
        report, report_result = self._parse_writing_response(report_response, "full_report")
        if not report:
            raise ValueError("Writer 没有生成报告内容")

        state.outline = normalized_outline
        state.draft_sections = draft_sections
        state.final_report = report
        self._merge_report_references(state, report_result.get("references", []))
        state.phase = "writing"
        return state

    async def revise(self, state: ResearchState) -> ResearchState:
        """审核后的报告修订模式，对齐 LeadWriter 的 revision 分支。"""

        if not state.final_report.strip():
            raise ValueError("没有可供修订的报告")
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
            system_prompt=self.SECTION_WRITING_SYSTEM,
            user_prompt=self._render_prompt(self.REVISION_PROMPT, payload),
        )
        revised, revision_result = self._parse_writing_response(
            revised_response, "revised_content"
        )
        if not revised:
            raise ValueError("Writer 没有生成修订内容")
        state.final_report = revised
        addressed = revision_result.get("addressed_issues", [])
        if isinstance(addressed, list):
            addressed_ids = {str(item).strip() for item in addressed}
            for issue in state.critic_feedback:
                if issue.get("id") in addressed_ids:
                    issue["resolved"] = True
        state.phase = "revising"
        return state

    @staticmethod
    def _parse_writing_response(response: str, field: str) -> tuple[str, dict]:
        """Interpret structured Writer output; local mock text remains accepted."""

        raw = response.strip()
        match = re.fullmatch(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
        candidate = match.group(1) if match else raw
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return raw, {}
        if not isinstance(parsed, dict):
            raise ValueError("Writer 返回的结构化结果必须是对象")
        content = parsed.get(field)
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"Writer 返回结果缺少 {field}")
        return content.strip(), parsed

    @staticmethod
    def _merge_report_references(state: ResearchState, references: object) -> None:
        if not isinstance(references, list):
            return
        known_urls = {str(item.get("url", "")).strip() for item in state.references}
        allowed_urls = {str(item.get("url", "")).strip() for item in state.raw_sources}
        for reference in references:
            if not isinstance(reference, dict):
                continue
            url = str(reference.get("url", "")).strip()
            if not url or url not in allowed_urls or url in known_urls:
                continue
            state.references.append(reference)
            known_urls.add(url)

    @staticmethod
    def _charts_for_section(charts: list[dict], section_id: str) -> list[dict]:
        related = [
            chart
            for chart in charts
            if not chart.get("section_id") or str(chart.get("section_id")).strip() == section_id
        ]
        return related[:10]

    @staticmethod
    def _facts_for_section(
        facts: list[dict],
        section_id: str,
    ) -> list[dict]:
        """优先选择当前章节的事实；没有关联时回退到全部事实。"""
        related = [
            fact
            for fact in facts
            if str(fact.get("section_id", "")).strip() == section_id
        ]
        return related or facts

    @staticmethod
    def _merge_facts(*groups: list[dict]) -> list[dict]:
        """合并事实并按来源和内容去重。"""
        merged: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for group in groups:
            for fact in group:
                key = (
                    str(fact.get("source_url", "")).strip(),
                    str(fact.get("content", "")).strip(),
                )
                if key not in seen:
                    seen.add(key)
                    merged.append(fact)
        return merged
