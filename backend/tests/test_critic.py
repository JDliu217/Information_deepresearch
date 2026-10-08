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


class LowScorePassClient(MockLLMClient):
    async def complete_json(self, role, payload):
        result = await super().complete_json(role, payload)
        if role == "critic":
            result["overall_assessment"]["quality_score"] = 5.0
            result["quality_score"] = 5.0
        return result


class CriticAgentTests(unittest.TestCase):
    def test_critic_context_uses_reference_summary_limits(self):
        class CapturingCriticClient(MockLLMClient):
            def __init__(self):
                self.payload = None

            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.payload = payload
                return await super().complete_json(role, payload, system_prompt, user_prompt)

        async def run():
            client = CapturingCriticClient()
            state = ResearchState("测试问题")
            state.final_report = "报告" * 5000
            state.outline = [{"id": "sec-1", "title": "章节", "status": "drafted"}]
            state.draft_sections = {"sec-1": "草稿" * 5000}
            state.facts = [
                {"id": f"fact-{i}", "content": "事实" * 200, "source_title": "来源", "confidence": 0.8}
                for i in range(25)
            ]
            state.data_points = [{"id": f"dp-{i}", "name": "指标", "value": i} for i in range(20)]
            state.raw_sources = [{"title": "来源", "url": f"https://example.com/{i}"} for i in range(40)]
            await CriticAgent(client).run(state)
            return client

        client = asyncio.run(run())
        self.assertLessEqual(len(client.payload["report"]), 8000)
        self.assertEqual(len(client.payload["facts"]), 20)
        self.assertTrue(all(len(fact["content"]) <= 150 for fact in client.payload["facts"]))
        self.assertEqual(len(client.payload["data_points"]), 15)
        self.assertEqual(set(client.payload["outline"][0]), {"id", "title", "status"})

    def test_critic_prompt_matches_reference_review_contract(self):
        class CapturingCriticClient(MockLLMClient):
            def __init__(self):
                self.system_prompt = ""
                self.user_prompt = ""

            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.system_prompt = system_prompt
                self.user_prompt = user_prompt
                return await super().complete_json(role, payload, system_prompt, user_prompt)

        async def run():
            client = CapturingCriticClient()
            state = ResearchState("测试问题")
            state.final_report = "报告 https://example.com"
            state.draft_sections = {"sec-1": "章节草稿"}
            state.outline = [{"id": "sec-1", "title": "章节", "status": "drafted"}]
            state.facts = [{"id": "fact-1", "content": "事实", "source_name": "来源", "confidence": 0.8}]
            await CriticAgent(client).run(state)
            return client

        client = asyncio.run(run())
        self.assertIn("零容忍幻觉", client.user_prompt)
        self.assertIn('"suggestion"', client.user_prompt)
        self.assertIn("issue_type", client.user_prompt)
        self.assertIn("strength_points", client.user_prompt)
        self.assertEqual(client.system_prompt, CriticAgent.REVIEW_SYSTEM)

    def test_critic_final_check_uses_reference_truncation_and_only_open_issues(self):
        class CapturingFinalCheckClient(MockLLMClient):
            def __init__(self):
                self.payload = None
                self.user_prompt = ""

            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.payload = payload
                self.user_prompt = user_prompt
                return {
                    "resolved_issues": [],
                    "unresolved_issues": [],
                    "new_issues": [],
                    "final_verdict": "approved",
                    "final_score": 8,
                    "publication_readiness": "ready",
                    "final_comments": "通过",
                }

        async def run():
            client = CapturingFinalCheckClient()
            state = ResearchState("测试问题")
            state.final_report = "修订报告" * 2000
            state.critic_feedback = [
                {"id": "issue-open", "severity": "major", "description": "缺少来源", "resolved": False},
                {"id": "issue-closed", "severity": "minor", "description": "已解决", "resolved": True},
            ]
            await CriticAgent(client).final_check(state)
            return client

        client = asyncio.run(run())
        self.assertEqual(len(client.payload["revised_content"]), 8000)
        self.assertIn("缺少来源", client.payload["previous_issues"])
        self.assertNotIn("已解决", client.payload["previous_issues"])
        self.assertIn("approved", client.user_prompt)

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
        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)
        self.assertEqual(state.review_result["issues"], [])

    def test_critic_rejects_invalid_result(self):
        state = ResearchState("测试问题")
        state.final_report = "## 报告\n内容"

        with self.assertRaisesRegex(ValueError, "verdict"):
            asyncio.run(CriticAgent(BrokenCriticClient()).run(state))

    def test_critic_requires_report(self):
        with self.assertRaisesRegex(ValueError, "审核的报告"):
            asyncio.run(CriticAgent(MockLLMClient()).run(ResearchState("测试问题")))

    def test_critic_preserves_pass_with_low_quality_score(self):
        state = ResearchState("测试问题")
        state.final_report = "## 报告\n内容 https://example.com"
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
        state.raw_sources = [{"url": "https://example.com"}]

        reviewed = asyncio.run(CriticAgent(LowScorePassClient()).run(state))

        # The reference Critic trusts the normalized model verdict.
        self.assertEqual(reviewed.review_result["verdict"], "pass")
        self.assertEqual(reviewed.review_result["quality_score"], 5.0)

    def test_critic_preserves_pass_with_unresolved_major_issue(self):
        class MajorIssueClient(MockLLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                result = await super().complete_json(role, payload, system_prompt, user_prompt)
                if role == "critic":
                    result["overall_assessment"]["verdict"] = "pass"
                    result["overall_assessment"]["quality_score"] = 8.0
                    result["issues"] = [{
                        "id": "major-1",
                        "issue_type": "missing_source",
                        "severity": "major",
                        "description": "缺少关键来源",
                        "suggestion": "补充来源",
                    }]
                return result

        state = ResearchState("测试问题")
        state.final_report = "报告 https://example.com"
        state.facts = [{"id": "fact-1", "content": "事实", "source_url": "https://example.com"}]
        state.raw_sources = [{"title": "来源", "url": "https://example.com"}]

        reviewed = asyncio.run(CriticAgent(MajorIssueClient()).run(state))

        self.assertEqual(reviewed.review_result["verdict"], "pass")
        self.assertEqual(reviewed.unresolved_issues, 1)
        self.assertEqual(reviewed.review_result["structured_issues"][0]["issue_type"], "missing_source")

    def test_critic_normalizes_common_model_format_variants(self):
        state = ResearchState("测试问题")
        state.facts = [{"id": "fact-1", "content": "事实"}]
        raw = {
            "overall_assessment": {
                "verdict": "通过",
                "quality_score": "8分",
                "summary": "主要结论有来源支持",
            },
            # Some models return a singleton object rather than a JSON list.
            "issues": {
                "type": "缺少来源",
                "severity": "low",
                "problem": "有一处数据需要补充出处",
                "recommendation": "增加来源链接",
                "target_section": "全局",
                "requires_new_search": "false",
                "search_query": ["公司年报 数据"],
            },
            "fact_check_results": {
                "id": "fact-1",
                "status": "待核实",
                "explanation": "还要对照原始材料",
            },
            "missing_aspects": "行业竞争格局",
            "strength_points": ["结构清晰", None],
            "needs_more_research": "false",
            "search_queries": "行业竞争格局 公开资料",
        }

        review = CriticAgent._validate_review(raw, state)

        self.assertEqual(review["verdict"], "pass")
        self.assertEqual(review["quality_score"], 8.0)
        self.assertEqual(review["missing_aspects"], ["行业竞争格局"])
        self.assertEqual(review["strengths"], ["结构清晰"])
        self.assertEqual(review["search_queries"], ["行业竞争格局 公开资料"])
        self.assertFalse(review["needs_more_research"])
        issue = review["structured_issues"][0]
        self.assertEqual(issue["issue_type"], "missing_source")
        self.assertEqual(issue["severity"], "minor")
        self.assertEqual(issue["target_section"], "global")
        self.assertFalse(issue["requires_new_search"])
        self.assertEqual(issue["search_query"], "公司年报 数据")
        self.assertEqual(review["fact_check_results"][0]["status"], "unverified")

    def test_critic_defaults_missing_verdict_to_revision(self):
        review = CriticAgent._validate_review({
            "overall_assessment": {"quality_score": 6, "summary": "需要补充证据"},
            "issues": [{"description": "证据不充分", "issue_type": "missing_source", "severity": "major"}],
        })

        self.assertEqual(review["verdict"], "needs_revision")
        self.assertEqual(review["structured_issues"][0]["suggestion"], "证据不充分")
        self.assertFalse(review["structured_issues"][0]["requires_new_search"])


if __name__ == "__main__":
    unittest.main()
