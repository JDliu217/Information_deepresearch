import asyncio
import json
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
    def test_report_draft_progress_includes_synthesis_summary_and_conclusions(self):
        class SynthesisMetadataClient(MockLLMClient):
            async def complete_text(
                self, role, payload, system_prompt="", user_prompt="", **kwargs
            ):
                if payload.get("mode") == "report":
                    return json.dumps(
                        {
                            "full_report": "完整报告",
                            "executive_summary": "报告摘要",
                            "conclusions": ["结论一", "结论二"],
                            "references": [],
                        },
                        ensure_ascii=False,
                    )
                return await super().complete_text(
                    role,
                    payload,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    **kwargs,
                )

        state = ResearchState("测试问题")
        state.outline = [{"id": "sec-1", "title": "章节一"}]
        asyncio.run(WriterAgent(SynthesisMetadataClient()).run(state))

        report_event = next(
            message for message in state.messages if message["type"] == "report_draft"
        )
        self.assertEqual(report_event["content"]["executive_summary"], "报告摘要")
        self.assertEqual(report_event["content"]["conclusions"], ["结论一", "结论二"])

    def test_mock_writer_returns_json_for_each_writer_mode(self):
        async def run():
            client = MockLLMClient()
            responses = {}
            for mode, payload in (
                ("section", {"query": "测试问题", "section": {"title": "章节"}}),
                ("report", {"query": "测试问题", "outline": [], "draft_sections": {}}),
                ("revision", {"query": "测试问题", "original_content": "报告"}),
            ):
                response = await client.complete_text(
                    "writer", {**payload, "mode": mode}, json_mode=True
                )
                responses[mode] = json.loads(response)
            return responses

        responses = asyncio.run(run())

        self.assertIn("content", responses["section"])
        self.assertIn("full_report", responses["report"])
        self.assertIn("revised_content", responses["revision"])

    def test_writer_revision_uses_bounded_report_feedback_and_new_facts(self):
        class CapturingWriterClient(MockLLMClient):
            def __init__(self):
                self.payload = None

            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                self.payload = payload
                return json.dumps({"revised_content": "修订后的报告"}, ensure_ascii=False)

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
        self.assertFalse(state.critic_feedback[0]["resolved"])
        self.assertEqual(state.phase, "reviewing")
        self.assertLessEqual(
            len(client.payload["original_content"]), WriterAgent.MAX_REVISION_REPORT_CHARS
        )
        self.assertEqual(len(client.payload["new_facts"]), 5)

    def test_writer_revision_includes_current_supplementary_facts_with_citations(self):
        class CapturingWriterClient(MockLLMClient):
            def __init__(self):
                self.payload = None
                self.user_prompt = ""

            async def complete_text(
                self, role, payload, system_prompt="", user_prompt="", **kwargs
            ):
                self.payload = payload
                self.user_prompt = user_prompt
                return json.dumps({"revised_content": "加入补充证据后的报告"}, ensure_ascii=False)

        async def run():
            client = CapturingWriterClient()
            state = ResearchState("测试问题")
            state.iteration = 1
            state.final_report = "完整报告" * 2000
            state.facts = [
                {"content": f"旧事实 {index}"}
                for index in range(8)
            ]
            state.facts.append(
                {
                    "content": "2024年营业收入为51.51亿元。",
                    "source_name": "公司业绩快报",
                    "source_url": "https://example.com/annual-report",
                    "metadata": {
                        "analysis_mode": "supplementary",
                        "research_iteration": 1,
                        "search_query": "公司2024年营业收入",
                    },
                }
            )
            await WriterAgent(client).revise(state)
            return client

        client = asyncio.run(run())
        self.assertEqual(len(client.payload["original_content"]), len("完整报告" * 2000))
        self.assertEqual(len(client.payload["new_facts"]), 1)
        self.assertIn("https://example.com/annual-report", client.user_prompt)
        self.assertIn("51.51亿元", client.user_prompt)

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
        self.assertIn("资深研究分析师", system_prompt)
        self.assertNotIn("AI芯片", section_prompt)
        self.assertNotIn("市场概况", section_prompt)

        report_payload, _, synthesis_prompt = client.prompts[-1]
        self.assertEqual(report_payload["mode"], "report")
        self.assertIn("使用层级编号", synthesis_prompt)
        self.assertIn("参考文献列表", synthesis_prompt)
        self.assertNotIn("AI芯片", synthesis_prompt)

    def test_writer_falls_back_to_drafted_sections_when_synthesis_json_is_incomplete(self):
        class IncompleteSynthesisClient(MockLLMClient):
            async def complete_text(
                self, role, payload, system_prompt="", user_prompt="", json_mode=False
            ):
                if payload.get("mode") == "report":
                    return (
                        '{"executive_summary": "摘要", "references": '
                        '[{"title": "不应追加", "url": "https://example.com"}]}'
                    )
                return await super().complete_text(
                    role, payload, system_prompt, user_prompt, json_mode=json_mode
                )

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
        self.assertEqual(result.references, [])

    def test_writer_rejects_citations_without_a_retrieved_source_url(self):
        class CitationClient(MockLLMClient):
            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                if payload.get("mode") == "section":
                    return (
                        '{"content":"正文","citations":['
                        '{"source":"未知","url":"https://untrusted.example"},'
                        '{"source":"未知","url":"https://untrusted.example"}]}'
                    )
                if payload.get("mode") == "report":
                    reference = {
                        "id": 10,
                        "title": "模型给出的来源",
                        "url": "https://also-untrusted.example",
                    }
                    return json.dumps(
                        {
                            "full_report": "完整报告",
                            "references": [reference, reference],
                        },
                        ensure_ascii=False,
                    )
                return await super().complete_text(role, payload, system_prompt, user_prompt)

        state = ResearchState("测试问题")
        state.outline = [{"id": "sec-1", "title": "章节一"}]
        state.facts = [{"content": "事实", "source_url": "https://example.com/source"}]
        result = asyncio.run(WriterAgent(CitationClient()).run(state))

        self.assertEqual(result.references, [])
        self.assertNotIn("https://untrusted.example", result.final_report)
        self.assertNotIn("https://also-untrusted.example", result.final_report)
        self.assertTrue(
            any(log.get("event") == "unsupported_citations_removed" for log in result.logs)
        )

    def test_writer_passes_fact_urls_to_section_prompt_and_keeps_verified_links(self):
        class CitationClient(MockLLMClient):
            async def complete_text(self, role, payload, system_prompt="", user_prompt="", **kwargs):
                if payload.get("mode") == "section":
                    self.section_prompt = user_prompt
                    return json.dumps(
                        {
                            "content": (
                                "事实来自[公司公告](https://example.com/notice)，"
                                "另一个引用[伪造来源](https://fake.example/report)。"
                            ),
                            "citations": [
                                {"source": "公司公告", "url": "https://example.com/notice"},
                                {"source": "伪造来源", "url": "https://fake.example/report"},
                            ],
                        },
                        ensure_ascii=False,
                    )
                if payload.get("mode") == "report":
                    return json.dumps({"full_report": ""}, ensure_ascii=False)
                return await super().complete_text(
                    role, payload, system_prompt, user_prompt, **kwargs
                )

        state = ResearchState("测试问题")
        state.outline = [{"id": "sec-1", "title": "章节一"}]
        state.raw_sources = [{"title": "公司公告", "url": "https://example.com/notice"}]
        state.facts = [
            {
                "id": "fact-1",
                "content": "有来源的事实",
                "source_name": "公司公告",
                "source_url": "https://example.com/notice",
                "section_id": "sec-1",
            }
        ]
        client = CitationClient()
        result = asyncio.run(WriterAgent(client).run(state))

        self.assertIn("https://example.com/notice", client.section_prompt)
        self.assertIn("[公司公告](https://example.com/notice)", result.final_report)
        self.assertNotIn("https://fake.example/report", result.final_report)
        self.assertEqual(
            [reference["url"] for reference in result.references],
            ["https://example.com/notice"],
        )

    def test_writer_does_not_cite_a_site_homepage_as_evidence(self):
        class HomepageClient(MockLLMClient):
            async def complete_text(self, role, payload, system_prompt="", user_prompt="", **kwargs):
                if payload.get("mode") == "section":
                    return json.dumps(
                        {
                            "content": "公司收入见[公司网站](https://example.com/)。",
                            "citations": [
                                {"source": "公司网站", "url": "https://example.com/"}
                            ],
                        },
                        ensure_ascii=False,
                    )
                if payload.get("mode") == "report":
                    return json.dumps(
                        {
                            "full_report": "公司收入见[公司网站](https://example.com/)。",
                            "references": [
                                {"title": "公司网站", "url": "https://example.com/"}
                            ],
                        },
                        ensure_ascii=False,
                    )
                return await super().complete_text(
                    role, payload, system_prompt, user_prompt, **kwargs
                )

        state = ResearchState("测试问题")
        state.outline = [{"id": "sec-1", "title": "经营情况"}]
        state.raw_sources = [{"title": "公司网站", "url": "https://example.com/"}]
        state.facts = [
            {
                "content": "公司收入有相关报道",
                "source_name": "公司网站",
                "source_url": "https://example.com/",
                "section_id": "sec-1",
            }
        ]
        result = asyncio.run(WriterAgent(HomepageClient()).run(state))

        self.assertNotIn("](https://example.com/)", result.final_report)
        self.assertIn("站点首页/栏目页不能核验具体事实", result.final_report)
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

    def test_writer_rejects_non_json_text_as_structured_output(self):
        content, result = WriterAgent._parse_writing_response(
            "这是一段普通文本，不是 JSON。", "content"
        )

        self.assertEqual(content, "")
        self.assertEqual(result, {})

    def test_writer_parser_accepts_json_embedded_in_model_prose(self):
        content, result = WriterAgent._parse_writing_response(
            '结果如下： {"content":"章节正文"}', "content"
        )

        self.assertEqual(content, "章节正文")
        self.assertEqual(result, {"content": "章节正文"})


if __name__ == "__main__":
    unittest.main()
