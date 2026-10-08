import asyncio
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.graph.runtime import create_research_runtime
from app.persistence.base import Base
from app.persistence.repository import ResearchRepository


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


if __name__ == "__main__":
    unittest.main()
