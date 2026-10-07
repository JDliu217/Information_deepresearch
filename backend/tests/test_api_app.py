import unittest

from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.main import create_app
from app.api.schemas import ResearchRequest


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


class ApiAppTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self):
        client = TestClient(create_app())

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_research_request_validates_non_empty_query(self):
        with self.assertRaises(ValidationError):
            ResearchRequest(query="")

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



if __name__ == "__main__":
    unittest.main()
