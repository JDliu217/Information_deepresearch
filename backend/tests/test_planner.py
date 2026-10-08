import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.domain.state import ResearchState


class BrokenPlannerClient(LLMClient):
    def __init__(self):
        self.calls = []
        self.responses = [
            {"outline": [], "research_questions": []},
            {"outline": ["not a section"] * 3, "research_questions": []},
            {"outline": [], "research_questions": []},
        ]

    async def complete_json(
        self, role, payload, system_prompt="", user_prompt="", temperature=None, max_tokens=None
    ):
        self.calls.append({
            "role": role,
            "payload": payload,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        })
        return self.responses[len(self.calls) - 1]

    async def complete_text(
        self, role, payload, system_prompt="", user_prompt="", temperature=None,
        max_tokens=None, json_mode=False
    ):
        return ""


class PlannerAgentTests(unittest.TestCase):
    def test_planner_accepts_reference_flat_plan_contract(self):
        class FlatPlannerClient(LLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.user_prompt = user_prompt
                return {
                    "research_subject": "王维",
                    "hypothesis_1": "王维的创作受到时代与个人经历影响",
                    "sec_1_title": "发展历程",
                    "sec_1_desc": "梳理王维一生中的关键阶段",
                    "sec_1_query": "王维 生平发展历程",
                    "sec_2_title": "业务变化",
                    "sec_2_desc": "分析王维创作与经历的变化",
                    "sec_2_query": "王维 创作经历变化",
                    "sec_3_title": "未来趋势",
                    "sec_3_desc": "评价王维作品的文学影响",
                    "sec_3_query": "王维 文学影响",
                    "questions": "经历了哪些阶段？;未来趋势是什么？",
                }

            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                return ""

        async def run():
            client = FlatPlannerClient()
            state = ResearchState("介绍一下诗人王维的一生")
            await PlannerAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())
        self.assertEqual([section["id"] for section in state.outline], ["sec_1", "sec_2", "sec_3"])
        self.assertEqual(state.outline[0]["search_queries"], ["王维 生平发展历程"])
        self.assertFalse(state.outline[0]["requires_data"])
        self.assertFalse(state.outline[0]["requires_chart"])
        self.assertEqual(state.hypotheses[0]["content"], "王维的创作受到时代与个人经历影响")
        self.assertEqual(state.research_questions, ["经历了哪些阶段？", "未来趋势是什么？"])
        self.assertIn("介绍一下诗人王维的一生", client.user_prompt)
        self.assertIn('"outline"', client.user_prompt)
        self.assertNotIn("市场概况", client.user_prompt)

    def test_planner_prompt_is_topic_driven_for_a_biography(self):
        class CapturingPlannerClient(LLMClient):
            def __init__(self):
                self.system_prompt = ""
                self.user_prompt = ""

            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.system_prompt = system_prompt
                self.user_prompt = user_prompt
                return {
                    "research_subject": "王维",
                    "outline": [
                        {"title": title, "description": "围绕王维及其生平研究。", "search_queries": [query]}
                        for title, query in (
                            ("生平经历", "王维 生平经历"),
                            ("时代背景", "王维 所处时代"),
                            ("作品与影响", "王维 代表作品 文学影响"),
                        )
                    ],
                    "research_questions": ["王维经历了哪些重要阶段？"],
                    "hypotheses": [],
                    "key_entities": ["王维"],
                }

            async def complete_text(self, role, payload, system_prompt="", user_prompt="", **kwargs):
                return ""

        async def run():
            client = CapturingPlannerClient()
            state = ResearchState("介绍一下诗人王维的一生")
            await PlannerAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())

        self.assertEqual(state.outline[0]["title"], "生平经历")
        self.assertIn("介绍一下诗人王维的一生", client.user_prompt)
        self.assertIn("人物研究可按生平阶段", client.user_prompt)
        self.assertIn("不能把问题改成另一个主题", client.user_prompt)
        self.assertIn("research_subject填写用户问题中直接出现的核心对象名称", client.user_prompt)
        self.assertNotIn("市场概况", client.user_prompt)
        self.assertNotIn("AI芯片", client.user_prompt)

    def test_planner_retries_when_model_changes_the_research_subject(self):
        class DriftingPlannerClient(LLMClient):
            def __init__(self):
                self.calls = []

            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.calls.append(user_prompt)
                if len(self.calls) == 1:
                    subject = "人工智能"
                    titles = ["市场概况", "竞争格局", "技术趋势"]
                else:
                    subject = "王维"
                    titles = ["生平经历", "时代背景", "作品与影响"]
                return {
                    "research_subject": subject,
                    "outline": [
                        {
                            "title": title,
                            "description": f"围绕{subject}整理证据。",
                            "search_queries": [f"{subject} {title}"],
                        }
                        for title in titles
                    ],
                    "research_questions": [f"{subject}有哪些重要信息？"],
                    "key_entities": [subject],
                }

            async def complete_text(self, role, payload, system_prompt="", user_prompt="", **kwargs):
                return ""

        async def run():
            client = DriftingPlannerClient()
            state = ResearchState("介绍一下诗人王维的一生")
            await PlannerAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())

        self.assertEqual(len(client.calls), 2)
        self.assertEqual(state.outline[0]["title"], "生平经历")
        self.assertTrue(
            all(
                "王维" in query
                for section in state.outline
                for query in section["search_queries"]
            )
        )

    def test_planner_retries_legacy_flat_plan_without_a_research_subject(self):
        class LegacyThenStructuredClient(LLMClient):
            def __init__(self):
                self.calls = 0

            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.calls += 1
                if self.calls == 1:
                    return {
                        "sec_1_title": "市场概况",
                        "sec_1_desc": "分析市场规模",
                        "sec_1_query": "AI 市场规模",
                        "sec_2_title": "竞争格局",
                        "sec_2_desc": "分析企业竞争",
                        "sec_2_query": "AI 企业竞争",
                        "sec_3_title": "技术趋势",
                        "sec_3_desc": "分析技术趋势",
                        "sec_3_query": "AI 技术趋势",
                    }
                return {
                    "research_subject": "王维",
                    "outline": [
                        {
                            "title": title,
                            "description": f"围绕王维研究{title}。",
                            "search_queries": [f"王维 {title}"],
                        }
                        for title in ("生平经历", "时代背景", "作品与影响")
                    ],
                }

            async def complete_text(self, role, payload, system_prompt="", user_prompt="", **kwargs):
                return ""

        async def run():
            client = LegacyThenStructuredClient()
            state = ResearchState("介绍一下诗人王维的一生")
            await PlannerAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())

        self.assertEqual(client.calls, 2)
        self.assertEqual(state.outline[0]["title"], "生平经历")

    def test_planner_revision_uses_reference_context_without_consuming_prompt_queries(self):
        class RevisionClient(MockLLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                if payload.get("current_outline"):
                    self.assert_revision_payload = payload
                    self.assert_revision_system_prompt = system_prompt
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
        self.assertEqual(
            client.assert_revision_system_prompt,
            "你是总架构师，需要判断是否需要调整研究计划。",
        )

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

    def test_planner_records_error_after_three_invalid_plans(self):
        state = ResearchState("测试问题")
        client = BrokenPlannerClient()

        result = asyncio.run(PlannerAgent(client).run(state))

        self.assertIs(result, state)
        self.assertEqual(len(client.calls), 3)
        self.assertEqual(state.errors, ["Failed to generate research plan after retries"])
        self.assertEqual(state.phase, "init")
        retry_prompt = client.calls[1]["user_prompt"]
        self.assertIn('"key_entities": []', retry_prompt)
        self.assertIn("测试问题", retry_prompt)
        self.assertNotIn("市场概况", retry_prompt)
        self.assertNotIn('"hypotheses"', retry_prompt)


if __name__ == "__main__":
    unittest.main()
