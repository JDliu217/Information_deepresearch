import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.workflow.research_workflow import ResearchWorkflow


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


async def collect_events(workflow, query, session_id=None):
    return [
        event
        async for event in workflow.stream(query, session_id=session_id)
    ]


class StreamWorkflowTests(unittest.TestCase):
    def test_stream_emits_ordered_events_and_final_result(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

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
                "plan_ready",
                "phase_started",
                "research_evidence_ready",
                "phase_started",
                "draft_ready",
                "phase_started",
                "review_completed",
                "research_completed",
            ],
        )
        self.assertTrue(all(event["session_id"] == "stream-001" for event in events))
        self.assertEqual(events[1]["phase"], "planning")
        self.assertEqual(events[3]["phase"], "researching")
        self.assertEqual(events[4]["source_count"], 3)
        self.assertEqual(events[4]["fact_count"], 3)
        self.assertEqual(events[-1]["phase"], "completed")
        self.assertIn("## 执行摘要", events[-1]["report"])
        self.assertEqual(events[-1]["quality_score"], 8.0)
        self.assertEqual(len(events[-1]["references"]), 3)

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
        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)

        events = asyncio.run(collect_events(workflow, "新能源汽车行业趋势"))

        evidence_events = [
            event for event in events if event["type"] == "research_evidence_ready"
        ]
        self.assertEqual(len(evidence_events), 2)
        self.assertFalse(evidence_events[0]["supplementary"])
        self.assertTrue(evidence_events[1]["supplementary"])
        self.assertEqual(evidence_events[1]["iteration"], 1)
        self.assertEqual(events[-1]["type"], "research_completed")
        self.assertEqual(events[-1]["review"]["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
