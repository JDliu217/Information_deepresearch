import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.state import ResearchState
from app.persistence.base import Base
from app.persistence.repository import ResearchRepository


class PersistenceRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()
        self.repository = ResearchRepository(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_save_and_load_state_round_trip(self):
        state = ResearchState("测试问题", session_id="session-1")
        state.outline = [{"id": "sec_1", "title": "现状"}]
        state.final_report = "报告内容"
        state.phase = "completed"
        state.quality_score = 8.0
        state.review_result = {"verdict": "pass"}

        self.repository.save_state(state)
        loaded = self.repository.load_state("session-1")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.query, "测试问题")
        self.assertEqual(loaded.outline, state.outline)
        self.assertEqual(loaded.final_report, "报告内容")
        self.assertEqual(loaded.review_result["verdict"], "pass")

    def test_events_are_appended_and_read_in_sequence(self):
        state = ResearchState("测试问题", session_id="session-1")
        self.repository.save_state(state)

        first = self.repository.append_event(
            {
                "type": "research_started",
                "session_id": "session-1",
                "phase": "init",
                "iteration": 0,
                "query": "测试问题",
                "max_iterations": 1,
            }
        )
        second = self.repository.append_event(
            {
                "type": "phase_started",
                "session_id": "session-1",
                "phase": "planning",
                "iteration": 0,
                "agent": "planner",
            }
        )

        self.assertEqual((first.sequence, second.sequence), (0, 1))
        events = self.repository.list_events("session-1")
        self.assertEqual([event["type"] for event in events], [
            "research_started",
            "phase_started",
        ])

    def test_append_event_requires_existing_run(self):
        with self.assertRaisesRegex(ValueError, "研究任务不存在"):
            self.repository.append_event(
                {
                    "type": "research_started",
                    "session_id": "missing",
                    "phase": "init",
                    "iteration": 0,
                    "query": "测试问题",
                    "max_iterations": 1,
                }
            )


if __name__ == "__main__":
    unittest.main()
