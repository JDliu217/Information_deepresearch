"""研究报告写作 Agent。"""

from __future__ import annotations

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """根据研究计划和带来源事实生成 Markdown 报告。"""

    name = "writer"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.plan:
            raise ValueError("没有可用于写作的研究计划")
        if not state.facts:
            raise ValueError("没有可用于写作的事实")

        report = await self.llm.complete_text(
            role=self.name,
            payload={
                "query": state.query,
                "plan": state.plan,
                "facts": state.facts,
                "references": state.references,
                "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告。",
            },
        )
        report = report.strip()
        if not report:
            raise ValueError("Writer 没有生成报告内容")

        state.final_report = report
        state.phase = "writing"
        return state
