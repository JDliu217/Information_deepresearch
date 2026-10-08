import asyncio
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.llm_client import MockLLMClient
from app.core.run_control import CANCELLED, InMemoryRunControlStore
from app.core.search_client import MockSearchClient
from app.domain.events import EVENT_TYPES, ResearchEventType
from app.graph.runtime import create_research_runtime
from app.persistence.base import Base
from app.persistence.repository import ResearchRepository


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


async def next_agent_progress(stream, message_type):
    """Skip already queued progress and return the requested agent message."""
    while True:
        event = await anext(stream)
        if (
            event["type"] == ResearchEventType.AGENT_PROGRESS
            and event.get("message_type") == message_type
        ):
            return event


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


class PausedSearchClient(MockSearchClient):
    def __init__(self):
        self.search_started = asyncio.Event()
        self.release_search = asyncio.Event()

    async def search(self, query, limit=3):
        self.search_started.set()
        await self.release_search.wait()
        return await super().search(query, limit)


class PausedWriterLLM(MockLLMClient):
    def __init__(self):
        self.writer_started = asyncio.Event()
        self.release_writer = asyncio.Event()
        self.paused = False

    async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
        if role == "writer" and payload.get("mode") == "section" and not self.paused:
            self.paused = True
            self.writer_started.set()
            await self.release_writer.wait()
        return await super().complete_text(role, payload, system_prompt, user_prompt)


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

        milestones = [
            event
            for event in events
            if event["type"] in EVENT_TYPES
            and event["type"] != ResearchEventType.AGENT_PROGRESS
        ]
        self.assertEqual(
            [event["type"] for event in milestones],
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
        self.assertEqual(milestones[1]["phase"], "planning")
        self.assertEqual(len(milestones[2]["outline"]), 3)
        self.assertEqual(milestones[2]["hypotheses"][0]["status"], "unverified")
        self.assertEqual(milestones[3]["phase"], "researching")
        self.assertEqual(milestones[4]["source_count"], 3)
        self.assertEqual(milestones[4]["fact_count"], 3)
        self.assertEqual(milestones[5]["phase"], "analyzing")
        self.assertEqual(milestones[6]["insight_count"], 1)
        self.assertEqual(milestones[6]["chart_count"], 1)
        self.assertEqual(milestones[6]["code_execution_count"], 1)
        self.assertEqual(milestones[6]["code_executions"][0]["status"], "succeeded")
        self.assertEqual(milestones[10]["unresolved_issues"], 0)
        self.assertEqual(len(milestones[10]["fact_check_results"]), 3)
        progress = [
            event for event in events
            if event["type"] == ResearchEventType.AGENT_PROGRESS
            and event["message_type"] == "search_progress"
        ]
        self.assertEqual(len(progress), 3)
        self.assertEqual(progress[0]["phase"], "researching")
        section_events = [
            event for event in events
            if event["type"] == ResearchEventType.AGENT_PROGRESS
            and event["message_type"] == "section_content"
        ]
        self.assertEqual(len(section_events), 3)
        self.assertTrue(all(event["phase"] == "writing" for event in section_events))
        self.assertTrue(
            any(
                event["message_type"] == "report_draft"
                for event in events
                if event["type"] == ResearchEventType.AGENT_PROGRESS
            )
        )
        self.assertEqual(
            set(milestones[8]["draft_sections"]),
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertEqual(milestones[-1]["phase"], "completed")
        self.assertIn("## 执行摘要", milestones[-1]["report"])
        self.assertEqual(milestones[-1]["quality_score"], 8.0)
        self.assertEqual(len(milestones[-1]["references"]), 3)
        self.assertEqual(len(milestones[-1]["insights"]), 1)
        self.assertEqual(len(milestones[-1]["data_points"]), 4)
        self.assertEqual(len(milestones[-1]["charts"]), 1)
        self.assertEqual(len(milestones[-1]["code_executions"]), 1)

    def test_search_progress_streams_while_search_is_still_running(self):
        search = PausedSearchClient()
        workflow = create_research_runtime(MockLLMClient(), search)

        async def inspect_stream():
            stream = workflow.stream("测试问题")
            for expected in ("research_started", "phase_started", "outline_ready", "phase_started"):
                event = await anext(stream)
                self.assertEqual(event["type"], expected)
            # The researcher emits a running step before launching parallel
            # section searches. Each section emits its own action event.
            first_progress = await anext(stream)
            self.assertEqual(first_progress["type"], ResearchEventType.AGENT_PROGRESS)
            self.assertEqual(first_progress["message_type"], "research_step")
            waiting_for_progress = asyncio.create_task(
                next_agent_progress(stream, "search_progress")
            )
            await search.search_started.wait()
            self.assertFalse(waiting_for_progress.done())
            search.release_search.set()
            progress = await waiting_for_progress
            self.assertEqual(progress["phase"], "researching")
            _ = [event async for event in stream]

        asyncio.run(inspect_stream())

    def test_cancel_waits_for_search_node_boundary_after_agent_progress(self):
        search = PausedSearchClient()
        control = InMemoryRunControlStore()
        workflow = create_research_runtime(
            MockLLMClient(), search, run_control=control
        )

        async def inspect_stream():
            stream = workflow.stream("测试问题", session_id="cancel-search-001")
            action = None
            while action is None:
                event = await anext(stream)
                if (
                    event["type"] == ResearchEventType.AGENT_PROGRESS
                    and event["message_type"] == "action"
                ):
                    action = event
            workflow.request_cancel("cancel-search-001")
            waiting_for_progress = asyncio.create_task(
                next_agent_progress(stream, "search_progress")
            )
            await search.search_started.wait()
            self.assertFalse(waiting_for_progress.done())
            search.release_search.set()
            progress = await waiting_for_progress
            self.assertEqual(progress["message_type"], "search_progress")
            remaining = [event async for event in stream]
            self.assertTrue(
                any(
                    event.get("message_type") == "search_progress"
                    for event in remaining
                    if event["type"] == ResearchEventType.AGENT_PROGRESS
                )
            )
            self.assertNotIn(
                "research_evidence_ready",
                [event["type"] for event in remaining],
            )

        asyncio.run(inspect_stream())
        self.assertEqual(control.get("cancel-search-001").status, CANCELLED)

    def test_section_content_streams_before_writer_finishes(self):
        llm = PausedWriterLLM()
        workflow = create_research_runtime(llm, MockSearchClient())

        async def inspect_stream():
            stream = workflow.stream("测试问题")
            action_seen = False
            while not action_seen:
                event = await anext(stream)
                if (
                    event["type"] == ResearchEventType.AGENT_PROGRESS
                    and event["message_type"] == "action"
                    and event.get("phase") == "writing"
                ):
                    action_seen = True
            waiting_for_section = asyncio.create_task(anext(stream))
            await llm.writer_started.wait()
            self.assertFalse(waiting_for_section.done())
            llm.release_writer.set()
            section_event = await waiting_for_section
            self.assertEqual(section_event["type"], ResearchEventType.AGENT_PROGRESS)
            self.assertEqual(section_event["message_type"], "section_content")
            self.assertEqual(section_event["phase"], "writing")
            self.assertTrue(section_event["content"]["content"])
            _ = [event async for event in stream]

        asyncio.run(inspect_stream())

    def test_incremental_agent_progress_is_persisted_as_typed_events(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine, expire_on_commit=False)()
        try:
            repository = ResearchRepository(session)
            workflow = create_research_runtime(
                MockLLMClient(),
                MockSearchClient(),
                repository=repository,
            )
            asyncio.run(collect_events(workflow, "测试问题", session_id="stream-persist-001"))

            persisted = repository.list_events("stream-persist-001")
            progress_types = [
                event["message_type"]
                for event in persisted
                if event["type"] == ResearchEventType.AGENT_PROGRESS
            ]
            self.assertIn("search_progress", progress_types)
            self.assertIn("search_results", progress_types)
            self.assertIn("section_content", progress_types)
        finally:
            session.close()
            engine.dispose()

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
