"""研究信息收集 Agent。"""

from __future__ import annotations

from app.core.search_client import SearchClient
from app.domain.state import ResearchState

from .base import BaseAgent


class ResearcherAgent(BaseAgent):
    """根据研究子问题收集候选来源。

    这一版只负责搜索和去重。事实提取会在后续步骤使用 LLM 单独完成，
    这样每个 Agent 的输入和输出都更容易观察。
    """

    name = "researcher"

    def __init__(self, search: SearchClient, results_per_question: int = 3):
        if results_per_question < 1:
            raise ValueError("results_per_question 必须大于 0")
        self.search = search
        self.results_per_question = results_per_question

    async def run(self, state: ResearchState) -> ResearchState:
        """搜索所有子问题，并把来源写入共享状态。"""
        if state.pending_search_queries:
            questions = [query.strip() for query in state.pending_search_queries]
        else:
            questions = [question.strip() for question in state.research_questions]
        questions = [question for question in questions if question]
        if not questions:
            raise ValueError("没有可执行的研究子问题")

        collected_sources = list(state.sources)
        for question in questions:
            results = await self.search.search(
                query=question,
                limit=self.results_per_question,
            )
            collected_sources.extend(result.to_dict() for result in results)

        state.sources = self._deduplicate_sources(collected_sources)
        state.references = [
            {
                "title": source["title"],
                "url": source["url"],
            }
            for source in state.sources
            if source.get("url")
        ]
        state.pending_search_queries = []
        state.phase = "researching"
        return state

    @staticmethod
    def _deduplicate_sources(sources: list[dict]) -> list[dict]:
        """按 URL 去重，同时保留第一次出现的顺序。"""
        unique: dict[str, dict] = {}
        for source in sources:
            url = str(source.get("url", "")).strip()
            if url and url not in unique:
                unique[url] = source
        return list(unique.values())
