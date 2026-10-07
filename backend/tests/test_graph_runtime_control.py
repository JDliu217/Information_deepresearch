import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.run_control import CANCELLED, COMPLETED, FAILED, InMemoryRunControlStore
from app.core.search_client import MockSearchClient
from app.graph.runtime import create_research_runtime


class GraphRuntimeControlTests(unittest.TestCase):
    def test_run_marks_completed_status(self):
        control = InMemoryRunControlStore()
        runtime = create_research_runtime(
            MockLLMClient(), MockSearchClient(), run_control=control
        )

        state = asyncio.run(runtime.run("测试问题", session_id="control-1"))

        status = control.get("control-1")
        self.assertEqual(state.phase, "completed")
        self.assertEqual(status.status, COMPLETED)
        self.assertEqual(status.phase, "completed")

    def test_stream_stops_at_node_boundary_after_cancel_request(self):
        control = InMemoryRunControlStore()
        runtime = create_research_runtime(
            MockLLMClient(), MockSearchClient(), run_control=control
        )

        async def collect_events():
            events = []
            async for event in runtime.stream("测试问题", session_id="control-2"):
                events.append(event)
                if event["type"] == "research_started":
                    runtime.request_cancel("control-2")
            return events

        events = asyncio.run(collect_events())

        self.assertEqual(control.get("control-2").status, CANCELLED)
        self.assertEqual(events[0]["type"], "research_started")
        self.assertNotIn("research_completed", [event["type"] for event in events])

    def test_failed_run_marks_failed_status(self):
        control = InMemoryRunControlStore()
        runtime = create_research_runtime(
            MockLLMClient(), MockSearchClient(), run_control=control
        )

        with self.assertRaisesRegex(ValueError, "研究问题不能为空"):
            asyncio.run(runtime.run("", session_id="control-3"))

        status = control.get("control-3")
        self.assertEqual(status.status, FAILED)
        self.assertIn("研究问题不能为空", status.error)


if __name__ == "__main__":
    unittest.main()
