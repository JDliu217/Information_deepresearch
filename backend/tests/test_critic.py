import asyncio
import unittest

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenCriticClient(LLMClient):
    async def complete_json(self, role, payload):
        return {"verdict": "unknown", "quality_score": 20, "issues": "错误格式"}

    async def complete_text(self, role, payload):
        return ""


class CriticAgentTests(unittest.TestCase):
    def test_critic_approves_source_grounded_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await WriterAgent(llm).run(state)
            await CriticAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "reviewing")
        self.assertEqual(state.review["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)
        self.assertEqual(state.review["issues"], [])

    def test_critic_rejects_invalid_result(self):
        state = ResearchState("测试问题")
        state.final_report = "## 报告\n内容"

        with self.assertRaisesRegex(ValueError, "verdict"):
            asyncio.run(CriticAgent(BrokenCriticClient()).run(state))

    def test_critic_requires_report(self):
        with self.assertRaisesRegex(ValueError, "审核的报告"):
            asyncio.run(CriticAgent(MockLLMClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
