"""研究信息收集 Agent。"""

from __future__ import annotations

from app.core.search_client import SearchClient
from app.domain.state import ResearchState

from .base import BaseAgent


class ResearcherAgent(BaseAgent):
    """根据章节大纲中的搜索查询收集候选来源。

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
        """搜索章节查询，并把来源与章节关联后写入共享状态。"""
        if state.pending_search_queries:
            tasks = [
                {"query": query.strip(), "section_id": "", "section_title": ""}
                for query in state.pending_search_queries
            ]
        else:
            tasks = self._build_search_tasks(state)
        tasks = [task for task in tasks if task["query"]]
        if not tasks:
            raise ValueError("没有可执行的研究子问题")

        collected_sources = list(state.raw_sources)
        for task in tasks:
            results = await self.search.search(
                query=task["query"],
                limit=self.results_per_question,
            )
            for result in results:
                source = result.to_dict()
                if task["section_id"]:
                    source["section_id"] = task["section_id"]
                    source["section_title"] = task["section_title"]
                collected_sources.append(source)

        state.raw_sources = self._deduplicate_sources(collected_sources)
        state.references = [
            {
                "title": source["title"],
                "url": source["url"],
            }
            for source in state.raw_sources
            if source.get("url")
        ]
        state.pending_search_queries = []
        state.phase = "researching"
        return state

    @staticmethod
    def _build_search_tasks(state: ResearchState) -> list[dict[str, str]]:
        """把章节大纲转换成搜索任务；没有大纲时回退到研究问题。"""
        tasks: list[dict[str, str]] = []
        for section in state.outline:
            section_id = str(section.get("id", "")).strip()
            section_title = str(section.get("title", "")).strip()
            queries = section.get("search_queries") or [section_title]
            if not isinstance(queries, list):
                raise ValueError("章节 search_queries 必须是列表")
            for query in queries:
                query = str(query).strip()
                if query:
                    tasks.append(
                        {
                            "query": query,
                            "section_id": section_id,
                            "section_title": section_title,
                        }
                    )

        if tasks:
            return tasks

        return [
            {"query": str(question).strip(), "section_id": "", "section_title": ""}
            for question in state.research_questions
        ]

    @staticmethod
    def _deduplicate_sources(sources: list[dict]) -> list[dict]:
        """按 URL 去重，同时保留第一次出现的顺序。"""
        unique: dict[str, dict] = {}
        for source in sources:
            url = str(source.get("url", "")).strip()
            if url and url not in unique:
                unique[url] = source
        return list(unique.values())
