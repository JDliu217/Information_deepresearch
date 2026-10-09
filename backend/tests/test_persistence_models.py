import unittest

from sqlalchemy import create_engine, inspect

from app.persistence.base import Base
from app.persistence.database import DatabaseSettings, create_session_factory
from app.persistence.models import ResearchEventRecord, ResearchRunRecord
from app.persistence.serialization import event_to_record, state_to_dict
from app.domain.state import ResearchState


class PersistenceModelTests(unittest.TestCase):
    def test_models_create_on_sqlite_for_local_contract_tests(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)

        tables = set(inspect(engine).get_table_names())

        self.assertEqual(tables, {"research_runs", "research_events"})
        self.assertIsNotNone(ResearchRunRecord.__table__.c.state_data)
        self.assertIsNotNone(ResearchRunRecord.__table__.c.status)
        self.assertIsNotNone(ResearchRunRecord.__table__.c.error)
        self.assertIsNotNone(ResearchEventRecord.__table__.c.data)

    def test_state_serializes_all_domain_fields(self):
        state = ResearchState("测试问题", session_id="session-1")
        serialized = state_to_dict(state)

        self.assertEqual(serialized["session_id"], "session-1")
        self.assertIn("outline", serialized)
        self.assertIn("review_result", serialized)

    def test_event_serialization_validates_domain_event_shape(self):
        record = event_to_record(
            {
                "type": "research_started",
                "session_id": "session-1",
                "phase": "init",
                "iteration": 0,
                "query": "测试问题",
                "max_iterations": 1,
            }
        )

        self.assertEqual(record["event_type"], "research_started")
        self.assertEqual(record["data"]["query"], "测试问题")

    def test_database_settings_can_be_loaded_without_connecting(self):
        settings = DatabaseSettings(url="sqlite://")
        factory = create_session_factory(create_engine(settings.url))

        with factory() as session:
            self.assertTrue(session.is_active)


if __name__ == "__main__":
    unittest.main()
