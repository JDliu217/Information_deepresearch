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
    def test_planner_accepts_reference_flat_plan_contract(self):
        class FlatPlannerClient(LLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.user_prompt = user_prompt
                return {
                    "hypothesis_1": "增长受市场需求影响",
                    "sec_1_title": "发展历程",
                    "sec_1_desc": "梳理关键阶段",
                    "sec_1_query": "发展历程",
                    "sec_2_title": "业务变化",
                    "sec_2_desc": "分析业务变化",
                    "sec_2_query": "业务变化",
                    "sec_3_title": "未来趋势",
                    "sec_3_desc": "判断未来方向",
                    "sec_3_query": "未来趋势",
                    "questions": "经历了哪些阶段？;未来趋势是什么？",
                }

            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                return ""

        async def run():
            client = FlatPlannerClient()
            state = ResearchState("测试课题")
            await PlannerAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())
        self.assertEqual([section["id"] for section in state.outline], ["sec_1", "sec_2", "sec_3"])
        self.assertEqual(state.outline[0]["search_queries"], ["发展历程"])
        self.assertEqual(state.hypotheses[0]["content"], "增长受市场需求影响")
        self.assertEqual(state.research_questions, ["经历了哪些阶段？", "未来趋势是什么？"])
        self.assertIn('"sec_1_title"', client.user_prompt)

    def test_planner_revision_uses_reference_context_without_consuming_prompt_queries(self):
        class RevisionClient(MockLLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                if payload.get("current_outline"):
                    self.assert_revision_payload = payload
                    return {
                        "needs_revision": False,
                        "new_search_queries": ["缺口查询", "缺口查询"],
                    }
                return await super().complete_json(role, payload, system_prompt, user_prompt)

        async def run():
            state = ResearchState("测试问题")
            client = RevisionClient()
            await PlannerAgent(client).run(state)
            state.facts = [{"content": "新发现"}]
            await PlannerAgent(client).revise(state)
            return state, client

        state, client = asyncio.run(run())
        self.assertEqual(state.pending_search_queries, [])
        self.assertEqual(client.assert_revision_payload["completed_sections"], 0)
        self.assertIn("新发现", client.assert_revision_payload["new_findings"])
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
