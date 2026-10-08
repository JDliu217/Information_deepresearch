import unittest

from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.main import create_app
from app.api.schemas import ResearchRequest
from app.core.run_control import InMemoryRunControlStore


class FakeRuntime:
    def __init__(self):
        self.calls = []

    async def stream(self, query: str, *, session_id: str) -> AsyncIterator[dict]:
        self.calls.append((query, session_id))
        yield {
            "type": "research_started",
            "session_id": session_id,
            "phase": "init",
            "iteration": 0,
            "query": query,
            "max_iterations": 1,
        }
        yield {
            "type": "research_completed",
            "session_id": session_id,
            "phase": "completed",
            "iteration": 0,
            "report": "测试报告",
        }

    def can_resume(self, session_id: str) -> bool:
        return session_id == "resume-session"

    async def resume_stream(self, session_id: str) -> AsyncIterator[dict]:
        yield {
            "type": "research_completed",
            "session_id": session_id,
            "phase": "completed",
            "iteration": 0,
            "report": "恢复后的报告",
        }


class ApiAppTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self):
        client = TestClient(create_app())

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_research_request_validates_non_empty_query(self):
        with self.assertRaises(ValidationError):
            ResearchRequest(query="")

    def test_research_request_rejects_query_replaced_by_question_marks(self):
        with self.assertRaisesRegex(ValidationError, "UTF-8"):
            ResearchRequest(query="???????????")

    def test_research_request_rejects_query_with_most_characters_replaced(self):
        with self.assertRaisesRegex(ValidationError, "UTF-8"):
            ResearchRequest(query="????B??")

    def test_research_stream_returns_sse_frames(self):
        runtime = FakeRuntime()
        client = TestClient(create_app(runtime=runtime))

        response = client.post(
            "/api/research/stream",
            json={"query": "测试问题", "session_id": "api-session"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        self.assertEqual(response.headers["x-research-session-id"], "api-session")
        self.assertIn("event: research_started\n", response.text)
        self.assertIn('"query":"测试问题"', response.text)
        self.assertIn("event: research_completed\n", response.text)
        self.assertEqual(runtime.calls, [("测试问题", "api-session")])

    def test_research_stream_rejects_corrupted_query_before_starting_runtime(self):
        runtime = FakeRuntime()
        client = TestClient(create_app(runtime=runtime))

        response = client.post(
            "/api/research/stream",
            json={"query": "???????????", "session_id": "bad-encoding"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("UTF-8", response.text)
        self.assertEqual(runtime.calls, [])

    def test_status_and_cancel_endpoints_use_run_control(self):
        control = InMemoryRunControlStore()
        control.start("status-session")
        client = TestClient(create_app(run_control=control))

        status = client.get("/api/research/status-session/status")
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json()["status"], "running")

        cancelled = client.post("/api/research/status-session/cancel")
        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.json()["status"], "cancel_requested")

    def test_status_and_cancel_return_not_found_for_unknown_run(self):
        client = TestClient(create_app(run_control=InMemoryRunControlStore()))

        self.assertEqual(client.get("/api/research/missing/status").status_code, 404)
        self.assertEqual(client.post("/api/research/missing/cancel").status_code, 404)

    def test_events_endpoint_requires_repository(self):
        client = TestClient(create_app())

        response = client.get("/api/research/session/events")

        self.assertEqual(response.status_code, 503)

    def test_resume_endpoint_returns_sse_for_existing_checkpoint(self):
        client = TestClient(create_app(runtime=FakeRuntime()))

        response = client.post("/api/research/resume-session/resume")

        self.assertEqual(response.status_code, 200)
        self.assertIn("event: research_completed\n", response.text)
        self.assertIn("恢复后的报告", response.text)

    def test_resume_endpoint_returns_not_found_without_checkpoint(self):
        client = TestClient(create_app(runtime=FakeRuntime()))

        response = client.post("/api/research/missing/resume")

        self.assertEqual(response.status_code, 404)

    def test_injected_runtime_reuses_its_run_control_store(self):
        control = InMemoryRunControlStore()
        runtime = type("Runtime", (), {"run_control": control, "repository": None})()
        control.start("injected-session")
        client = TestClient(create_app(runtime=runtime))

        response = client.get("/api/research/injected-session/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "running")



if __name__ == "__main__":
    unittest.main()
