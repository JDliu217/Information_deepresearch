"""把多个 Agent 编排成一次完整研究任务。"""

from __future__ import annotations

from uuid import uuid4

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
from app.domain.state import ResearchState


class ResearchWorkflow:
    """Iteration 01 的最小同步编排器。

    每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
    后续再在这个类上增加流式事件和审核修订循环。
    """

    def __init__(
        self,
        llm: LLMClient,
        search: SearchClient,
        results_per_question: int = 3,
    ):
        self.planner = PlannerAgent(llm)
        self.researcher = ResearcherAgent(search, results_per_question)
        self.fact_extractor = FactExtractorAgent(llm)
        self.writer = WriterAgent(llm)
        self.critic = CriticAgent(llm)

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        """执行一次完整研究并返回最终状态。"""
        state = ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
        )

        await self.planner.run(state)
        await self.researcher.run(state)
        await self.fact_extractor.run(state)
        await self.writer.run(state)
        await self.critic.run(state)

        state.phase = "completed"
        return state
