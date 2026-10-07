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
    def test_planner_revision_uses_progress_and_appends_new_queries(self):
        class RevisionClient(MockLLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                if payload.get("current_outline"):
                    return {
                        "needs_revision": False,
                        "new_search_queries": ["缺口查询", "缺口查询"],
                    }
                return await super().complete_json(role, payload, system_prompt, user_prompt)

        async def run():
            state = ResearchState("测试问题")
            await PlannerAgent(RevisionClient()).run(state)
            state.facts = [{"content": "新发现"}]
            await PlannerAgent(RevisionClient()).revise(state)
            return state

        state = asyncio.run(run())
        self.assertEqual(state.pending_search_queries, ["缺口查询"])
    def test_planner_writes_outline_into_state(self):
        state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
        agent = PlannerAgent(MockLLMClient())

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "planning")
        self.assertEqual(len(result.outline), 3)
        self.assertEqual(len(result.research_questions), 3)
        self.assertEqual(result.outline[0]["id"], "sec_1")
        self.assertEqual(result.outline[0]["status"], "pending")
        self.assertEqual(len(result.hypotheses), 1)
        self.assertEqual(result.hypotheses[0]["status"], "unverified")
        self.assertIn("新能源汽车", result.outline[0]["description"])

    def test_planner_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            asyncio.run(PlannerAgent(MockLLMClient()).run(ResearchState("   ")))

    def test_planner_rejects_invalid_llm_result(self):
        with self.assertRaisesRegex(ValueError, "非空列表"):
            asyncio.run(PlannerAgent(BrokenPlannerClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
