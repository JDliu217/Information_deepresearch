import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.core.search_client import SearchClient, SearchResult
from app.domain.state import ResearchState


class ResearcherAgentTests(unittest.TestCase):
    def test_researcher_runs_three_section_searches_concurrently_in_stable_order(self):
        class ConcurrentSearch(SearchClient):
            def __init__(self):
                self.active = 0
                self.max_active = 0

            async def search(self, query, limit=3):
                self.active += 1
                self.max_active = max(self.max_active, self.active)
                try:
                    # Reverse completion order to verify deterministic merging.
                    await asyncio.sleep((4 - int(query[-1])) * 0.01)
                    return [
                        SearchResult(
                            title=query,
                            url=f"https://example.com/{query}",
                            snippet="摘要",
                            query=query,
                        )
                    ]
                finally:
                    self.active -= 1

        async def run():
            search = ConcurrentSearch()
            state = ResearchState("测试问题")
            state.outline = [
                {
                    "id": f"sec-{index}",
                    "title": f"章节 {index}",
                    "status": "pending",
                    "search_queries": [f"查询 {index}"],
                }
                for index in range(1, 5)
            ]
            await ResearcherAgent(search).run(state)
            return state, search

        state, search = asyncio.run(run())

        self.assertEqual(search.max_active, 3)
        self.assertEqual(
            [source["section_id"] for source in state.raw_sources],
            ["sec-1", "sec-2", "sec-3"],
        )
        self.assertTrue(
            all(source["analysis_mode"] == "normal" for source in state.raw_sources)
        )

    def test_researcher_limits_normal_run_to_three_pending_sections_and_ten_results(self):
        class CapturingSearch(SearchClient):
            def __init__(self):
                self.calls = []

            async def search(self, query, limit=3):
                self.calls.append((query, limit))
                return [
                    SearchResult(
                        title=f"来源 {index}",
                        url=f"https://example.com/{query}/{index}",
                        snippet="摘要",
                        query=query,
                    )
                    for index in range(2)
                ]

        async def run():
            search = CapturingSearch()
            state = ResearchState("测试问题")
            state.outline = [
                {
                    "id": f"sec-{index}",
                    "title": f"章节 {index}",
                    "status": "pending",
                    "search_queries": [f"查询 {index}"],
                }
                for index in range(5)
            ]
            await ResearcherAgent(search).run(state)
            return state, search

        state, search = asyncio.run(run())

        self.assertEqual(len(search.calls), 3)
        self.assertTrue(all(limit == 10 for _, limit in search.calls))
        self.assertEqual(
            {section["id"] for section in state.outline if section["status"] == "researching"},
            {"sec-0", "sec-1", "sec-2"},
        )
        self.assertEqual(len(state.raw_sources), 6)

    def test_researcher_limits_supplementary_queries_to_five(self):
        class CapturingSearch(SearchClient):
            def __init__(self):
                self.calls = []

            async def search(self, query, limit=3):
                self.calls.append((query, limit))
                return [SearchResult("来源", f"https://example.com/{query}", "摘要", query)]

        async def run():
            search = CapturingSearch()
            state = ResearchState("测试问题")
            state.pending_search_queries = [f"补充查询 {index}" for index in range(8)]
            await ResearcherAgent(search).run(state, supplementary=True)
            return state, search

        state, search = asyncio.run(run())
        self.assertEqual(len(search.calls), 5)
        self.assertTrue(all(limit == 8 for _, limit in search.calls))
        self.assertTrue(
            all(source["analysis_mode"] == "supplementary" for source in state.raw_sources)
        )

    def test_researcher_limits_recursive_queries_by_reference_type(self):
        class CapturingSearch(SearchClient):
            def __init__(self):
                self.calls = []

            async def search(self, query, limit=3):
                self.calls.append((query, limit))
                return [SearchResult("来源", f"https://example.com/{query}", "摘要", query)]

        state = ResearchState("测试问题")
        state.pending_search_queries = [f"追溯 {i}" for i in range(3)] + [
            f"线索 {i}" for i in range(3)
        ]
        state.pending_search_contexts = {
            query: [{"search_type": "source_tracing" if query.startswith("追溯") else "follow_up"}]
            for query in state.pending_search_queries
        }
        search = CapturingSearch()

        asyncio.run(ResearcherAgent(search).run(state, supplementary=True, recursive=True))

        self.assertEqual(
            [query for query, _ in search.calls],
            ["追溯 0", "追溯 1", "线索 0", "线索 1"],
        )
        self.assertTrue(all(limit == 6 for _, limit in search.calls))
        self.assertTrue(
            all(source["analysis_mode"] == "recursive" for source in state.raw_sources)
        )
    def test_researcher_collects_sources_after_planning(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.research_questions), 3)
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.references), 3)
        self.assertTrue(all(source["url"].startswith("https://") for source in state.raw_sources))
        self.assertEqual(
            {source["section_id"] for source in state.raw_sources},
            {"sec_1", "sec_2", "sec_3"},
        )

    def test_researcher_uses_all_queries_from_a_section(self):
        async def run():
            state = ResearchState("测试问题")
            state.outline = [
                {
                    "id": "sec-market",
                    "title": "市场规模",
                    "search_queries": ["市场规模 2024", "市场规模 2025"],
                }
            ]
            return await ResearcherAgent(MockSearchClient()).run(state)

        state = asyncio.run(run())

        self.assertEqual(len(state.raw_sources), 2)
        self.assertEqual(
            {source["query"] for source in state.raw_sources},
            {"市场规模 2024", "市场规模 2025"},
        )
        self.assertTrue(
            all(source["section_id"] == "sec-market" for source in state.raw_sources)
        )

    def test_researcher_deduplicates_existing_source_urls(self):
        async def run():
            state = ResearchState("测试问题")
            state.research_questions = ["相同问题", "相同问题"]
            return await ResearcherAgent(MockSearchClient()).run(state)

        state = asyncio.run(run())

        self.assertEqual(len(state.raw_sources), 1)
        self.assertEqual(len(state.references), 1)

    def test_researcher_rejects_missing_questions(self):
        state = ResearchState("还没有规划的问题")

        with self.assertRaisesRegex(ValueError, "研究子问题"):
            asyncio.run(ResearcherAgent(MockSearchClient()).run(state))


if __name__ == "__main__":
    unittest.main()
