import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.domain.state import ResearchState


class BrokenPlannerClient(LLMClient):
    async def complete_json(self, role, payload):
        return {"outline": [], "research_questions": []}

    async def complete_text(self, role, payload):
        return ""


class PlannerAgentTests(unittest.TestCase):
    def test_planner_writes_outline_into_state(self):
        state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
        agent = PlannerAgent(MockLLMClient())

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "planning")
        self.assertEqual(len(result.outline), 3)
        self.assertEqual(len(result.research_questions), 3)
        self.assertIn("新能源汽车", result.outline[0]["description"])

    def test_planner_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            asyncio.run(PlannerAgent(MockLLMClient()).run(ResearchState("   ")))

    def test_planner_rejects_invalid_llm_result(self):
        with self.assertRaisesRegex(ValueError, "非空列表"):
            asyncio.run(PlannerAgent(BrokenPlannerClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
