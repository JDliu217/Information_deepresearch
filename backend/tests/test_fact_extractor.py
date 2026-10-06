import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenFactClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "facts": [
                {
                    "content": "这条事实引用了不存在的来源。",
                    "source_url": "https://unknown.example.com",
                    "confidence": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class FactExtractorAgentTests(unittest.TestCase):
    def test_fact_extractor_turns_sources_into_facts(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(MockLLMClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(all(fact["source_url"] for fact in state.facts))
        self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))

    def test_fact_extractor_rejects_unknown_source_url(self):
        state = ResearchState("测试问题")
        state.sources = [
            {
                "title": "已知来源",
                "url": "https://known.example.com",
                "snippet": "摘要",
            }
        ]

        with self.assertRaisesRegex(ValueError, "未知来源"):
            asyncio.run(FactExtractorAgent(BrokenFactClient()).run(state))

    def test_fact_extractor_requires_sources(self):
        with self.assertRaisesRegex(ValueError, "来源"):
            asyncio.run(FactExtractorAgent(MockLLMClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
