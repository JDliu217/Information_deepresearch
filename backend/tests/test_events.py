import unittest

from app.domain.events import (
    EVENT_TYPES,
    RESEARCH_PHASES,
    ResearchEvent,
    ResearchEventType,
)


class ResearchEventTests(unittest.TestCase):
    def test_event_type_constants_are_registered(self):
        self.assertIn(ResearchEventType.OUTLINE_READY, EVENT_TYPES)
        self.assertIn("planning", RESEARCH_PHASES)

    def test_event_to_dict_keeps_common_fields_and_data(self):
        event = ResearchEvent(
            type=ResearchEventType.OUTLINE_READY,
            session_id="session-001",
            phase="planning",
            iteration=0,
            data={"outline": [{"id": "sec-1"}]},
        )

        self.assertEqual(
            event.to_dict(),
            {
                "type": "outline_ready",
                "session_id": "session-001",
                "phase": "planning",
                "iteration": 0,
                "outline": [{"id": "sec-1"}],
            },
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


if __name__ == "__main__":
    unittest.main()
