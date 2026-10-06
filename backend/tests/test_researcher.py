import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class ResearcherAgentTests(unittest.TestCase):
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
