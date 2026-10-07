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

    def test_critic_rejects_pass_with_low_quality_score(self):
        state = ResearchState("测试问题")
        state.final_report = "## 报告\n内容 https://example.com"
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
        state.raw_sources = [{"url": "https://example.com"}]

        with self.assertRaisesRegex(ValueError, "不能低于 7"):
            asyncio.run(CriticAgent(LowScorePassClient()).run(state))

    def test_critic_rejects_pass_with_unresolved_major_issue(self):
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

        with self.assertRaisesRegex(ValueError, "不能存在未解决"):
            asyncio.run(CriticAgent(MajorIssueClient()).run(state))


if __name__ == "__main__":
    unittest.main()
