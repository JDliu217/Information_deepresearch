"""研究报告写作 Agent。"""

from __future__ import annotations

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """按章节整理事实，并生成带来源的 Markdown 报告。"""

    name = "writer"

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
            section_content = await self.llm.complete_text(
                role=self.name,
                payload={
                    "mode": "section",
                    "query": state.query,
                    "section": section,
                    "facts": related_facts,
                    "data_points": state.data_points,
                    "insights": state.insights,
                    "charts": state.charts,
                    "review_result": state.review_result,
                    "iteration": state.iteration,
                    "instruction": "只生成本章节正文，不要重复章节标题；每个事实都保留可点击来源链接。",
                },
            )
            section_content = section_content.strip()
            if not section_content:
                raise ValueError(f"Writer 没有生成章节内容: {section_title}")

            section["status"] = "drafted"
            draft_sections[section_id] = section_content
            normalized_outline.append(section)

        report = await self.llm.complete_text(
            role=self.name,
            payload={
                "mode": "report",
                "query": state.query,
                "outline": normalized_outline,
                "facts": state.facts,
                "draft_sections": draft_sections,
                "data_points": state.data_points,
                "insights": state.insights,
                "charts": state.charts,
                "references": state.references,
                "review_result": state.review_result,
                "iteration": state.iteration,
                "instruction": "整合各章节草稿，生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
            },
        )
        report = report.strip()
        if not report:
            raise ValueError("Writer 没有生成报告内容")

        state.outline = normalized_outline
        state.draft_sections = draft_sections
        state.final_report = report
        state.phase = "writing"
        return state

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
