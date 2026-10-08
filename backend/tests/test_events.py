import unittest

from app.domain.events import (
    EVENT_TYPES,
    EVENT_REQUIRED_FIELDS,
    RESEARCH_PHASES,
    ResearchEvent,
    ResearchEventType,
)
from app.persistence.serialization import event_to_record


class ResearchEventTests(unittest.TestCase):
    def test_event_type_constants_are_registered(self):
        self.assertIn(ResearchEventType.OUTLINE_READY, EVENT_TYPES)
        self.assertIn(ResearchEventType.ANALYSIS_READY, EVENT_TYPES)
        self.assertIn("fact_check_results", EVENT_REQUIRED_FIELDS[ResearchEventType.REVIEW_COMPLETED])
        self.assertIn("planning", RESEARCH_PHASES)
        self.assertIn(ResearchEventType.AGENT_PROGRESS, EVENT_TYPES)

    def test_event_to_dict_keeps_common_fields_and_data(self):
        event = ResearchEvent(
            type=ResearchEventType.OUTLINE_READY,
            session_id="session-001",
            phase="planning",
            data={
                "outline": [{"id": "sec-1"}],
                "research_questions": [],
                "hypotheses": [],
                "key_entities": [],
                "mind_map": {},
            },
        )
        self.assertEqual(
            event.to_dict(),
            {
                "type": "outline_ready",
                "session_id": "session-001",
                "phase": "planning",
                "iteration": 0,
                "outline": [{"id": "sec-1"}],
                "research_questions": [],
                "hypotheses": [],
                "key_entities": [],
                "mind_map": {},
            },
        )

    def test_agent_progress_event_keeps_reference_message_type(self):
        event = ResearchEvent(
            type=ResearchEventType.AGENT_PROGRESS,
            session_id="session-001",
            phase="researching",
            data={
                "agent": "researcher",
                "message_type": "search_progress",
                "timestamp": "2026-10-08T00:00:00+00:00",
                "content": {"query": "测试查询", "progress": "1/2"},
            },
        ).to_dict()

        self.assertEqual(event["type"], "agent_progress")
        self.assertEqual(event["message_type"], "search_progress")
        self.assertEqual(event["content"]["progress"], "1/2")
        record = event_to_record(event)
        self.assertEqual(record["event_type"], "agent_progress")
        self.assertEqual(record["data"]["message_type"], "search_progress")

    def test_each_event_type_declares_required_fields(self):
        self.assertEqual(set(EVENT_TYPES), set(EVENT_REQUIRED_FIELDS))
        self.assertTrue(
            all(fields for fields in EVENT_REQUIRED_FIELDS.values()),
        )

    def test_event_rejects_missing_business_fields(self):
        with self.assertRaisesRegex(ValueError, "outline_ready.*必需字段"):
            ResearchEvent(
                ResearchEventType.OUTLINE_READY,
                "session-001",
                "planning",
                data={"outline": []},
            )

    def test_event_rejects_unknown_type(self):
        with self.assertRaisesRegex(ValueError, "事件类型"):
            ResearchEvent("unknown", "session-001", "planning")

    def test_event_rejects_empty_session_id(self):
        with self.assertRaisesRegex(ValueError, "session_id"):
            ResearchEvent(ResearchEventType.PHASE_STARTED, "  ", "planning")

    def test_event_rejects_unknown_phase(self):
        with self.assertRaisesRegex(ValueError, "研究阶段"):
            ResearchEvent(ResearchEventType.PHASE_STARTED, "session-001", "unknown")

    def test_event_rejects_invalid_iteration(self):
        with self.assertRaisesRegex(ValueError, "iteration"):
            ResearchEvent(ResearchEventType.PHASE_STARTED, "session-001", "planning", -1)

    def test_event_rejects_non_dict_data(self):
        with self.assertRaisesRegex(ValueError, "data"):
            ResearchEvent(
                ResearchEventType.PHASE_STARTED,
                "session-001",
                "planning",
                data=[],
            )

    def test_event_data_cannot_replace_common_fields(self):
        with self.assertRaisesRegex(ValueError, "session_id"):
            ResearchEvent(
                ResearchEventType.PHASE_STARTED,
                "session-001",
                "planning",
                data={"agent": "planner", "session_id": "other-session"},
            )


if __name__ == "__main__":
    unittest.main()
