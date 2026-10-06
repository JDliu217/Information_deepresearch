import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class WriterAgentTests(unittest.TestCase):
    def test_writer_generates_cited_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await WriterAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "writing")
        self.assertTrue(state.final_report.startswith("## 执行摘要"))
        self.assertIn("研究发现", state.final_report)
        self.assertIn("https://example.com/research/", state.final_report)

    def test_writer_requires_outline(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]

        with self.assertRaisesRegex(ValueError, "研究大纲"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))

    def test_writer_requires_facts(self):
        state = ResearchState("测试问题")
        state.outline = [{"title": "章节", "description": "描述"}]

        with self.assertRaisesRegex(ValueError, "事实"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))


if __name__ == "__main__":
    unittest.main()
