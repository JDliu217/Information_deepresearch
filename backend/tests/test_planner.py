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
                    "hypothesis_1": "王维的创作受到时代与个人经历影响",
                    "sec_1_title": "发展历程",
                    "sec_1_desc": "梳理王维一生中的关键阶段",
                    "sec_1_query": "王维 生平发展历程",
                    "sec_2_title": "创作经历",
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
        self.assertTrue(state.outline[0]["requires_data"])
        self.assertTrue(state.outline[0]["requires_chart"])
        self.assertEqual(state.hypotheses[0]["content"], "王维的创作受到时代与个人经历影响")
        self.assertEqual(state.research_questions, ["经历了哪些阶段？", "未来趋势是什么？"])
        self.assertEqual(state.planner_diagnostics[0]["response_format"], "reference_flat")
        self.assertTrue(state.planner_diagnostics[0]["accepted"])
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
        self.assertIn("research_subject填写用户问题中的核心对象名称", client.user_prompt)
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
        self.assertIn("Planner 三次尝试均未通过大纲校验", state.errors[0])
        self.assertEqual(state.phase, "planning")
        self.assertEqual(len(state.planner_diagnostics), 3)
        self.assertFalse(state.planner_diagnostics[0]["accepted"])
        self.assertIn("章节数为 0", state.planner_diagnostics[0]["validation_error"])
        retry_prompt = client.calls[1]["user_prompt"]
        self.assertIn('"key_entities":', retry_prompt)
        self.assertIn("测试问题", retry_prompt)
        self.assertIn("章节数为 0", retry_prompt)
        self.assertNotIn("市场概况", retry_prompt)
        self.assertIn('"outline"', retry_prompt)

    def test_flat_reference_plan_infers_subject_from_query_and_keeps_reference_defaults(self):
        class FlatClient(LLMClient):
            async def complete_json(self, role, payload, **kwargs):
                return {
                    "sec_1_title": "行业供需",
                    "sec_1_desc": "分析东岳硅材所在有机硅行业的供需情况",
                    "sec_1_query": "东岳硅材 有机硅行业 供需",
                    "sec_2_title": "经营表现",
                    "sec_2_desc": "梳理东岳硅材近年的产能和经营表现",
                    "sec_2_query": "东岳硅材 产能 经营数据",
                    "sec_3_title": "价格走势",
                    "sec_3_desc": "分析有机硅价格变化及其对公司的影响",
                    "sec_3_query": "东岳硅材 有机硅价格走势",
                    "questions": "供需如何变化？;经营表现如何？",
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        state = ResearchState(
            "分析东岳硅材所在有机硅行业2021—2025年景气和东岳硅材经营表现"
        )
        asyncio.run(PlannerAgent(FlatClient()).run(state))

        self.assertEqual(len(state.outline), 3)
        self.assertEqual(state.outline[0]["requires_data"], True)
        self.assertEqual(state.outline[0]["requires_chart"], True)
        self.assertEqual(state.outline[2]["requires_data"], False)
        self.assertEqual(state.planner_diagnostics[0]["response_format"], "reference_flat")
        self.assertIn("东岳硅材", state.planner_diagnostics[0]["response_preview"])

    def test_topic_guard_allows_section_specific_terms_without_repeating_subject_everywhere(self):
        class RelevantPlannerClient(LLMClient):
            async def complete_json(self, role, payload, **kwargs):
                return {
                    "research_subject": "东岳硅材",
                    "outline": [
                        {
                            "title": "公司经营",
                            "description": "分析东岳硅材的经营和财务表现",
                            "search_queries": ["东岳硅材 营收 产能"],
                        },
                        {
                            "title": "行业供需",
                            "description": "结合公司业务分析有机硅行业供需",
                            "search_queries": ["有机硅行业 供需变化"],
                        },
                        {
                            "title": "产品价格",
                            "description": "评估产品价格变化对企业的影响",
                            "search_queries": ["有机硅价格走势"],
                        },
                    ],
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        state = ResearchState("分析东岳硅材所在有机硅行业的经营和价格走势")
        asyncio.run(PlannerAgent(RelevantPlannerClient()).run(state))

        self.assertEqual(len(state.outline), 3)
        self.assertEqual(len(state.planner_diagnostics), 1)
        self.assertTrue(state.planner_diagnostics[0]["accepted"])

    def test_topic_guard_accepts_composed_subject_from_real_company_query(self):
        class CompositeSubjectClient(LLMClient):
            async def complete_json(self, role, payload, **kwargs):
                return {
                    "research_subject": (
                        "东岳硅材所在有机硅行业2021—2025年的行业景气和市场走势"
                        "及东岳硅材经营表现"
                    ),
                    "outline": [
                        {
                            "title": "有机硅供需",
                            "description": "分析东岳硅材所在有机硅行业的供需和产能",
                            "search_queries": ["有机硅行业 2021 2025 供需 产能"],
                        },
                        {
                            "title": "价格走势",
                            "description": "分析有机硅价格变化与行业景气",
                            "search_queries": ["有机硅行业 2021 2025 价格走势"],
                        },
                        {
                            "title": "公司经营",
                            "description": "梳理东岳硅材的经营表现",
                            "search_queries": ["东岳硅材 2021 2025 营收 利润"],
                        },
                    ],
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        state = ResearchState(
            "分析东岳硅材所在有机硅行业 2021—2025 年的行业景气和市场走势，"
            "并结合东岳硅材同期的经营表现撰写详细报告；"
            "重点关注供需、价格、产能和企业经营数据。"
        )
        asyncio.run(PlannerAgent(CompositeSubjectClient()).run(state))

        self.assertEqual(len(state.outline), 3)
        self.assertEqual(len(state.planner_diagnostics), 1)
        self.assertTrue(state.planner_diagnostics[0]["accepted"])

    def test_topic_guard_does_not_use_unrelated_words_in_composed_subject_as_anchors(self):
        class SubjectWithUnrelatedTopicClient(LLMClient):
            async def complete_json(self, role, payload, **kwargs):
                return {
                    "research_subject": "王维与人工智能行业",
                    "outline": [
                        {
                            "title": title,
                            "description": "分析人工智能行业及其技术发展",
                            "search_queries": [f"人工智能行业 {title}"],
                        }
                        for title in ("市场规模", "竞争格局", "技术趋势")
                    ],
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        state = ResearchState("介绍一下王维的一生")
        asyncio.run(PlannerAgent(SubjectWithUnrelatedTopicClient()).run(state))

        self.assertEqual(state.outline, [])
        self.assertEqual(len(state.planner_diagnostics), 3)
        self.assertIn("关联不足", state.planner_diagnostics[-1]["validation_error"])

    def test_topic_guard_rejects_unrelated_plan_and_records_exact_reason(self):
        class OffTopicClient(LLMClient):
            async def complete_json(self, role, payload, **kwargs):
                return {
                    "research_subject": "王维",
                    "outline": [
                        {
                            "title": title,
                            "description": "分析全球人工智能市场和大模型发展",
                            "search_queries": [f"人工智能 {title}"],
                        }
                        for title in ("AI市场规模", "AI竞争格局", "AI技术趋势")
                    ],
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        state = ResearchState("介绍一下诗人王维的一生")
        asyncio.run(PlannerAgent(OffTopicClient()).run(state))

        self.assertEqual(len(state.planner_diagnostics), 3)
        self.assertTrue(all(not item["accepted"] for item in state.planner_diagnostics))
        self.assertIn("关联不足", state.planner_diagnostics[-1]["validation_error"])
        self.assertIn("最后一次拒绝原因", state.errors[-1])

    def test_topic_guard_rejects_plan_where_most_sections_drift_off_topic(self):
        class MostlyOffTopicClient(LLMClient):
            def __init__(self):
                self.calls = 0

            async def complete_json(self, role, payload, **kwargs):
                self.calls += 1
                if self.calls == 1:
                    sections = [
                        ("生平经历", "梳理王维的重要人生经历", "王维 生平经历"),
                        ("作品影响", "分析王维作品的文学影响", "王维 作品 文学影响"),
                        ("AI市场规模", "分析人工智能芯片市场规模", "AI芯片 市场规模"),
                        ("AI竞争格局", "分析人工智能芯片企业竞争", "AI芯片 企业竞争"),
                        ("AI技术趋势", "分析人工智能芯片技术趋势", "AI芯片 技术趋势"),
                        ("AI政策环境", "梳理人工智能产业政策环境", "人工智能 政策环境"),
                    ]
                else:
                    sections = [
                        (title, f"围绕王维研究{title}", f"王维 {title}")
                        for title in ("生平经历", "时代背景", "作品影响", "历史地位", "诗歌特色", "后世评价")
                    ]
                return {
                    "research_subject": "王维",
                    "outline": [
                        {
                            "title": title,
                            "description": description,
                            "search_queries": [query],
                        }
                        for title, description, query in sections
                    ],
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        client = MostlyOffTopicClient()
        state = ResearchState("介绍一下诗人王维的一生")
        asyncio.run(PlannerAgent(client).run(state))

        self.assertEqual(client.calls, 2)
        self.assertFalse(state.planner_diagnostics[0]["accepted"])
        self.assertIn("关联不足", state.planner_diagnostics[0]["validation_error"])
        self.assertTrue(state.planner_diagnostics[1]["accepted"])
        self.assertEqual(state.outline[0]["title"], "生平经历")

    def test_planner_retries_after_model_call_failure_and_records_each_attempt(self):
        class TemporarilyUnavailableClient(LLMClient):
            def __init__(self):
                self.calls = 0
                self.prompts = []

            async def complete_json(self, role, payload, **kwargs):
                self.calls += 1
                self.prompts.append(kwargs.get("user_prompt", ""))
                if self.calls == 1:
                    raise RuntimeError("temporary provider timeout")
                return {
                    "research_subject": "王维",
                    "outline": [
                        {
                            "title": title,
                            "description": f"围绕王维研究{title}。",
                            "search_queries": [f"王维 {title}"],
                        }
                        for title in ("生平经历", "时代背景", "作品影响")
                    ],
                }

            async def complete_text(self, role, payload, **kwargs):
                return ""

        client = TemporarilyUnavailableClient()
        state = ResearchState("介绍一下诗人王维的一生")
        asyncio.run(PlannerAgent(client).run(state))

        self.assertEqual(client.calls, 2)
        self.assertEqual(len(state.planner_diagnostics), 2)
        self.assertFalse(state.planner_diagnostics[0]["accepted"])
        self.assertIn("temporary provider timeout", state.planner_diagnostics[0]["validation_error"])
        self.assertIn("temporary provider timeout", client.prompts[1])
        self.assertTrue(state.planner_diagnostics[1]["accepted"])


if __name__ == "__main__":
    unittest.main()
