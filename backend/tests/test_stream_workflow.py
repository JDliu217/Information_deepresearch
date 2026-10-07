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

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)


class PausedPlannerLLM(MockLLMClient):
    def __init__(self):
        self.planner_started = asyncio.Event()
        self.release_planner = asyncio.Event()

    async def complete_json(self, role, payload):
        if role == "planner":
            self.planner_started.set()
            await self.release_planner.wait()
        return await super().complete_json(role, payload)


async def collect_events(workflow, query, session_id=None):
    return [
        event
        async for event in workflow.stream(query, session_id=session_id)
    ]


class GraphRuntimeStreamTests(unittest.TestCase):
    def test_phase_started_is_streamed_before_planner_finishes(self):
        llm = PausedPlannerLLM()
        workflow = create_research_runtime(llm, MockSearchClient())

        async def inspect_stream():
            stream = workflow.stream("测试问题")
            first = await anext(stream)
            second = await anext(stream)
            pending_outline = asyncio.create_task(anext(stream))
            await llm.planner_started.wait()

            self.assertEqual(first["type"], "research_started")
            self.assertEqual(second["type"], "phase_started")
            self.assertEqual(second["phase"], "planning")
            self.assertFalse(pending_outline.done())

            llm.release_planner.set()
            outline = await pending_outline
            remaining = [event async for event in stream]
            self.assertEqual(outline["type"], "outline_ready")
            self.assertEqual(remaining[-1]["type"], "research_completed")

        asyncio.run(inspect_stream())

    def test_stream_emits_ordered_events_and_final_result(self):
        workflow = create_research_runtime(MockLLMClient(), MockSearchClient())

        events = asyncio.run(
            collect_events(
                workflow,
                "中国新能源汽车行业的发展趋势是什么？",
                session_id="stream-001",
            )
        )

        self.assertEqual(
            [event["type"] for event in events],
            [
                "research_started",
                "phase_started",
                "outline_ready",
                "phase_started",
                "research_evidence_ready",
                "phase_started",
                "analysis_ready",
                "phase_started",
                "draft_ready",
                "phase_started",
                "review_completed",
                "research_completed",
            ],
        )
        self.assertTrue(all(event["session_id"] == "stream-001" for event in events))
        self.assertEqual(events[1]["phase"], "planning")
        self.assertEqual(len(events[2]["outline"]), 3)
        self.assertEqual(events[2]["hypotheses"][0]["status"], "unverified")
        self.assertEqual(events[3]["phase"], "researching")
        self.assertEqual(events[4]["source_count"], 3)
        self.assertEqual(events[4]["fact_count"], 3)
        self.assertEqual(events[5]["phase"], "analyzing")
        self.assertEqual(events[6]["insight_count"], 1)
        self.assertEqual(events[6]["chart_count"], 1)
        self.assertEqual(events[6]["code_execution_count"], 1)
        self.assertEqual(events[6]["code_executions"][0]["status"], "succeeded")
        self.assertEqual(events[10]["unresolved_issues"], 0)
        self.assertEqual(len(events[10]["fact_check_results"]), 3)
        self.assertEqual(
            set(events[8]["draft_sections"]),
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertEqual(events[-1]["phase"], "completed")
        self.assertIn("## 执行摘要", events[-1]["report"])
        self.assertEqual(events[-1]["quality_score"], 8.0)
        self.assertEqual(len(events[-1]["references"]), 3)
        self.assertEqual(len(events[-1]["insights"]), 1)
        self.assertEqual(len(events[-1]["data_points"]), 3)
        self.assertEqual(len(events[-1]["charts"]), 1)
        self.assertEqual(len(events[-1]["code_executions"]), 1)

    def test_stream_marks_supplementary_research_iteration(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=["补充最新行业数据"],
                    search_queries=["2025年新能源汽车行业数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        workflow = create_research_runtime(llm, MockSearchClient(), max_iterations=1)

        events = asyncio.run(collect_events(workflow, "新能源汽车行业趋势"))

        evidence_events = [
            event for event in events if event["type"] == "research_evidence_ready"
        ]
        self.assertEqual(len(evidence_events), 2)
        self.assertFalse(evidence_events[0]["supplementary"])
        self.assertTrue(evidence_events[1]["supplementary"])
        self.assertEqual(evidence_events[1]["iteration"], 1)
        self.assertEqual(events[-1]["type"], "research_completed")
        self.assertEqual(events[-1]["review_result"]["verdict"], "pass")
        self.assertEqual(events[-1]["unresolved_issues"], 0)


if __name__ == "__main__":
    unittest.main()
