import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from langgraph.checkpoint.memory import InMemorySaver
from app.core.run_control import CANCELLED, COMPLETED, FAILED, InMemoryRunControlStore
from app.core.search_client import MockSearchClient
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
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

    def test_cancelled_run_can_resume_from_memory_checkpoint(self):
        control = InMemoryRunControlStore()
        runtime = create_research_runtime(
            MockLLMClient(),
            MockSearchClient(),
            run_control=control,
            checkpointer=InMemorySaver(
                serde=JsonPlusSerializer(
                    allowed_msgpack_modules=[("app.domain.state", "ResearchState")]
                )
            ),
        )

        async def cancel_after_start():
            async for event in runtime.stream("测试问题", session_id="control-4"):
                if event["type"] == "research_started":
                    runtime.request_cancel("control-4")

        asyncio.run(cancel_after_start())
        self.assertEqual(control.get("control-4").status, CANCELLED)
        self.assertTrue(runtime.can_resume("control-4"))

        state = asyncio.run(runtime.resume("control-4"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(control.get("control-4").status, COMPLETED)
        self.assertFalse(runtime.can_resume("control-4"))


if __name__ == "__main__":
    unittest.main()
