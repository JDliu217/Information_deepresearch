import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.graph.runtime import create_research_runtime


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)
        self.writer_payloads = []

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)

    async def complete_text(
        self,
        role,
        payload,
        system_prompt="",
        user_prompt="",
        temperature=None,
        max_tokens=None,
        json_mode=False,
    ):
        self.writer_payloads.append(payload)
        return await super().complete_text(
            role,
            payload,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )


class StructuredRoutingLLM(SequencedReviewLLM):
    async def complete_json(self, role, payload):
        if role == "critic":
            result = await super().complete_json(role, payload)
            if result["verdict"] == "needs_revision":
                result["needs_more_research"] = False
                result["search_queries"] = []
                result["issues"] = [{
                    "id": "issue_logic",
                    "target_section": "sec_1",
                    "issue_type": "missing_source",
                    "severity": "major",
                    "description": "需要补充数据来源",
                    "suggestion": "搜索官方统计",
                    "requires_new_search": True,
                    "search_query": "官方统计数据",
                }]
            return result
        return await super().complete_json(role, payload)

class RecordingSearchClient(MockSearchClient):
    def __init__(self):
        self.queries = []

    async def search(self, query, limit=3):
        self.queries.append(query)
        return await super().search(query, limit)


class ResearchGraphRuntimeTests(unittest.TestCase):
    def test_workflow_runs_full_research_chain(self):
        workflow = create_research_runtime(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("中国新能源汽车行业的发展趋势是什么？")
        )

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.outline[0]["title"], "现状与定义")
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(state.final_report)
        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)
        self.assertEqual(len(state.insights), 1)
        # FactExtractor contributes source-linked points and DataAnalyst
        # performs a separate structured extraction pass over the facts.
        self.assertEqual(len(state.data_points), 4)
        self.assertEqual(len(state.charts), 1)
        self.assertEqual(len(state.code_executions), 1)
        self.assertEqual(state.code_executions[0]["status"], "succeeded")
        # CodeWizard's reference analysis execution is independent from the
        # ECharts chart generation pass; an execution ID is optional.
        self.assertIn("execution_id", state.charts[0])
        self.assertIn("## 代码分析", state.final_report)

    def test_workflow_preserves_explicit_session_id(self):
        workflow = create_research_runtime(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("测试问题", session_id="session-001")
        )

        self.assertEqual(state.session_id, "session-001")

    def test_critic_routes_to_supplementary_research_then_passes(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=[{
                        "issue_type": "outdated",
                        "severity": "major",
                        "description": "补充最新行业数据",
                        "requires_new_search": True,
                        "search_query": "2025年新能源汽车行业数据",
                    }],
                    search_queries=["2025年新能源汽车行业数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = create_research_runtime(llm, search, max_iterations=1)

        state = asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(len(search.queries), 4)  # 3 个初始问题 + 1 个补充查询
        self.assertEqual(search.queries[-1], "2025年新能源汽车行业数据")
        self.assertEqual(len(state.raw_sources), 4)
        self.assertEqual(len(state.facts), 4)
        self.assertIn("2025年新能源汽车行业数据", state.final_report)

    def test_critic_routes_to_writer_revision_without_new_search(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    issues=["补充结论与证据之间的说明"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = create_research_runtime(llm, search, max_iterations=1)

        state = asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(len(search.queries), 3)
        report_payloads = [
            payload for payload in llm.writer_payloads if payload.get("mode") == "report"
        ]
        self.assertEqual(len(report_payloads), 1)
        revision_payloads = [
            payload for payload in llm.writer_payloads if payload.get("mode") == "revision"
        ]
        self.assertEqual(len(revision_payloads), 1)
        self.assertIn(
            "补充结论与证据之间的说明",
            [issue["description"] for issue in revision_payloads[0]["feedback"]],
        )
        self.assertIn("补充结论与证据之间的说明", state.final_report)

    def test_workflow_stops_after_max_iterations(self):
        llm = SequencedReviewLLM(
            [
                review("needs_revision", issues=["第一轮问题"]),
                review("needs_revision", issues=["仍需改进"], score=5.0),
            ]
        )
        workflow = create_research_runtime(llm, MockSearchClient(), max_iterations=1)

        state = asyncio.run(workflow.run("测试行业", session_id="bounded"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(state.review_result["verdict"], "needs_revision")
        self.assertEqual(state.review_result["issues"], ["仍需改进"])
        self.assertEqual(
            len([payload for payload in llm.writer_payloads if payload.get("mode") == "report"]),
            1,
        )
        self.assertEqual(
            len([payload for payload in llm.writer_payloads if payload.get("mode") == "revision"]),
            1,
        )

    def test_workflow_allows_multiple_review_iterations(self):
        llm = SequencedReviewLLM(
            [review("needs_revision", issues=["继续修订"])] * 4
            + [review("pass", score=8.0)]
        )
        workflow = create_research_runtime(llm, MockSearchClient(), max_iterations=4)

        state = asyncio.run(workflow.run("测试行业"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.iteration, 4)
        self.assertEqual(state.review_result["verdict"], "pass")

    def test_workflow_uses_structured_issue_to_choose_search(self):
        llm = StructuredRoutingLLM(
            [
                review("needs_revision", issues=["旧格式问题"]),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = create_research_runtime(llm, search, max_iterations=1)

        asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(search.queries[-1], "官方统计数据")

    def test_workflow_rejects_negative_iteration_limit(self):
        with self.assertRaisesRegex(ValueError, "max_iterations"):
            create_research_runtime(MockLLMClient(), MockSearchClient(), max_iterations=-1)


if __name__ == "__main__":
    unittest.main()
