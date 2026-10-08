import asyncio
import unittest

from app.agents.data_analyst import DataAnalystAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class WriterAgentTests(unittest.TestCase):
    def test_writer_revision_uses_bounded_report_feedback_and_new_facts(self):
        class CapturingWriterClient(MockLLMClient):
            def __init__(self):
                self.payload = None

            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                self.payload = payload
                return "修订后的报告"

        async def run():
            client = CapturingWriterClient()
            state = ResearchState("测试问题")
            state.final_report = "报告内容" * 3000
            state.critic_feedback = [
                {"id": "issue-1", "description": "缺少来源", "resolved": False}
            ]
            state.facts = [{"content": f"事实 {index}"} for index in range(8)]
            await WriterAgent(client).revise(state)
            return state, client

        state, client = asyncio.run(run())
        self.assertEqual(state.final_report, "修订后的报告")
        self.assertEqual(state.phase, "reviewing")
        self.assertLessEqual(len(client.payload["original_content"]), 6000)
        self.assertEqual(len(client.payload["new_facts"]), 5)

    def test_writer_generates_cited_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await DataAnalystAgent(llm).run(state)
            state.insights = ["测试数据洞察"]
            state.charts = [{"id": "chart-1", "title": "测试图表", "chart_type": "bar"}]
            await WriterAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "reviewing")
        self.assertTrue(state.final_report.startswith("## 执行摘要"))
        self.assertIn("研究发现", state.final_report)
        self.assertIn("数据洞察", state.final_report)
        self.assertIn("图表", state.final_report)
        self.assertIn("https://example.com/research/", state.final_report)
        self.assertEqual(
            set(state.draft_sections),
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertTrue(all(section["status"] == "drafted" for section in state.outline))
        for section in state.outline:
            self.assertIn(section["title"], state.final_report)

    def test_writer_requires_outline(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]

        with self.assertRaisesRegex(ValueError, "研究大纲"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))

    def test_writer_without_facts_uses_reference_fallback(self):
        state = ResearchState("测试问题")
        state.outline = [{"title": "章节", "description": "描述"}]

        result = asyncio.run(WriterAgent(MockLLMClient()).run(state))

        self.assertTrue(result.final_report)
        self.assertIn("章节", result.draft_sections["sec_1"])
        self.assertEqual(result.phase, "reviewing")

    def test_writer_prompt_contains_reference_requirements_and_context_limits(self):
        class CapturingWriterClient(MockLLMClient):
            def __init__(self):
                self.prompts = []

            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                self.prompts.append((payload, system_prompt, user_prompt))
                return await super().complete_text(role, payload, system_prompt, user_prompt)

        async def run():
            client = CapturingWriterClient()
            state = ResearchState("测试问题")
            state.outline = [{"id": "sec-a", "title": "A 章节", "description": "A 描述", "section_type": "mixed"}]
            state.facts = [
                {
                    "id": f"fact-{index}",
                    "content": f"事实 {index}",
                    "source_name": "来源",
                    "source_url": f"https://example.com/{index}",
                    "section_id": "sec-a",
                }
                for index in range(12)
            ]
            state.data_points = [{"name": f"指标{i}", "value": i} for i in range(15)]
            state.insights = [f"洞察{i}" for i in range(8)]
            await WriterAgent(client).run(state)
            return client

        client = asyncio.run(run())
        section_payload, system_prompt, section_prompt = client.prompts[0]
        # LeadWriter passes all facts linked to the section; only the
        # unlinked-fact fallback is capped at ten.
        self.assertEqual(len(section_payload["facts"]), 12)
        self.assertEqual(len(section_payload["data_points"]), 10)
        self.assertEqual(len(section_payload["insights"]), 5)
        self.assertIn("相关事实", section_prompt)
        self.assertIn("500-1000 字", section_prompt)
        self.assertIn("可点击链接格式", section_prompt)
        self.assertIn("顶级的行业研究分析师", system_prompt)

        report_payload, _, synthesis_prompt = client.prompts[-1]
        self.assertEqual(report_payload["mode"], "report")
        self.assertIn("使用层级编号", synthesis_prompt)
        self.assertIn("参考文献列表", synthesis_prompt)

    def test_writer_falls_back_to_drafted_sections_when_synthesis_json_is_incomplete(self):
        class IncompleteSynthesisClient(MockLLMClient):
            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                if payload.get("mode") == "report":
                    return '{"executive_summary": "摘要"}'
                return await super().complete_text(role, payload, system_prompt, user_prompt)

        state = ResearchState("测试问题")
        state.outline = [{"id": "sec-1", "title": "章节一", "description": "描述"}]
        state.facts = [{
            "content": "有来源的事实",
            "source_title": "来源",
            "source_url": "https://example.com/source",
            "section_id": "sec-1",
        }]
        result = asyncio.run(WriterAgent(IncompleteSynthesisClient()).run(state))

        self.assertTrue(result.final_report.startswith("# 测试问题 研究报告"))
        self.assertIn("有来源的事实", result.final_report)

    def test_writer_skips_untrusted_citation_url(self):
        class CitationClient(MockLLMClient):
            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                if payload.get("mode") == "section":
                    return '{"content":"正文","citations":[{"source":"未知","url":"https://untrusted.example"}]}'
                return await super().complete_text(role, payload, system_prompt, user_prompt)

        state = ResearchState("测试问题")
        state.outline = [{"id": "sec-1", "title": "章节一"}]
        state.facts = [{"content": "事实", "source_url": "https://example.com/source"}]
        result = asyncio.run(WriterAgent(CitationClient()).run(state))

        self.assertEqual(result.references, [])

    def test_writer_prefers_facts_from_the_matching_section(self):
        async def run():
            state = ResearchState("测试问题")
            state.outline = [
                {"id": "sec-a", "title": "A 章节", "description": "A 描述"},
                {"id": "sec-b", "title": "B 章节", "description": "B 描述"},
            ]
            state.facts = [
                {
                    "content": "A 事实",
                    "source_title": "A 来源",
                    "source_url": "https://example.com/a",
                    "section_id": "sec-a",
                },
                {
                    "content": "B 事实",
                    "source_title": "B 来源",
                    "source_url": "https://example.com/b",
                    "section_id": "sec-b",
                },
            ]
            return await WriterAgent(MockLLMClient()).run(state)

        state = asyncio.run(run())

        self.assertIn("A 事实", state.draft_sections["sec-a"])
        self.assertNotIn("B 事实", state.draft_sections["sec-a"])
        self.assertIn("B 事实", state.draft_sections["sec-b"])
        self.assertNotIn("A 事实", state.draft_sections["sec-b"])


if __name__ == "__main__":
    unittest.main()
