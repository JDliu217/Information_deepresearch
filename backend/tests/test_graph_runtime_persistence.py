import asyncio
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.llm_client import MockLLMClient
from app.core.run_control import InMemoryRunControlStore
from app.core.search_client import MockSearchClient
from app.graph.runtime import ResearchGraphRuntime, create_research_runtime
from app.persistence.base import Base
from app.persistence.repository import ResearchRepository


class FailingGraph:
    def astream(self, *_args, **_kwargs):
        async def updates():
            raise RuntimeError("测试节点异常")
            yield {}

        return updates()


class GraphRuntimePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()
        self.repository = ResearchRepository(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_run_persists_final_state_and_all_graph_events(self):
        runtime = create_research_runtime(
            MockLLMClient(),
            MockSearchClient(),
            repository=self.repository,
        )

        state = asyncio.run(runtime.run("测试问题", session_id="persisted-1"))
        loaded = self.repository.load_state("persisted-1")
        events = self.repository.list_events("persisted-1")

        self.assertEqual(state.phase, "completed")
        self.assertEqual(loaded.phase, "completed")
        self.assertEqual(loaded.final_report, state.final_report)
        self.assertEqual(self.repository.load_run_status("persisted-1")["status"], "completed")
        self.assertEqual(events[0]["type"], "research_started")
        self.assertEqual(events[-1]["type"], "research_completed")
        # Agent-level progress is persisted as additional typed events. Keep
        # the stable node milestones as the contract, without fixing the
        # total count of progress messages.
        event_types = [event["type"] for event in events]
        for expected in (
            "research_started",
            "outline_ready",
            "research_evidence_ready",
            "analysis_ready",
            "draft_ready",
            "review_completed",
            "research_completed",
        ):
            self.assertIn(expected, event_types)
        self.assertGreaterEqual(len(events), 12)

    def test_failed_run_persists_status_error_and_failure_event(self):
        runtime = ResearchGraphRuntime(
            graph=FailingGraph(),
            repository=self.repository,
            run_control=InMemoryRunControlStore(),
        )

        with self.assertRaisesRegex(RuntimeError, "测试节点异常"):
            asyncio.run(runtime.run("测试失败追踪", session_id="failed-persisted"))

        status = self.repository.load_run_status("failed-persisted")
        events = self.repository.list_events("failed-persisted")
        self.assertEqual(status["status"], "failed")
        self.assertEqual(status["error"], "测试节点异常")
        self.assertEqual(events[-1]["type"], "research_failed")
        self.assertEqual(events[-1]["error"], "测试节点异常")

    def test_planner_failure_persists_each_attempt_response_and_rejection_reason(self):
        class InvalidPlannerClient(MockLLMClient):
            async def complete_json(self, role, payload, **kwargs):
                if role == "planner":
                    return {"outline": [], "research_questions": []}
                return await super().complete_json(role, payload, **kwargs)

        runtime = create_research_runtime(
            InvalidPlannerClient(),
            MockSearchClient(),
            repository=self.repository,
        )

        with self.assertRaisesRegex(ValueError, "Planner 三次尝试"):
            asyncio.run(runtime.run("介绍一下诗人王维的一生", session_id="planner-trace"))

        status = self.repository.load_run_status("planner-trace")
        state = self.repository.load_state("planner-trace")
        events = self.repository.list_events("planner-trace")
        self.assertEqual(status["status"], "failed")
        self.assertEqual(status["phase"], "planning")
        self.assertEqual(len(state.planner_diagnostics), 3)
        self.assertEqual(events[-1]["type"], "research_failed")
        self.assertEqual(len(events[-1]["planner_diagnostics"]), 3)
        self.assertIn("章节数为 0", events[-1]["planner_diagnostics"][0]["validation_error"])
        self.assertIn('"outline": []', events[-1]["planner_diagnostics"][0]["response_preview"])


if __name__ == "__main__":
    unittest.main()
