import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import create_app
from app.api.schemas import ResearchRequest
from app.core.llm_client import MockLLMClient
from app.core.run_control import InMemoryRunControlStore
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.graph.runtime import create_research_runtime
from app.persistence.base import Base
from app.persistence.repository import ResearchRepository


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


class FailingRuntime(FakeRuntime):
    def __init__(self, status=None):
        super().__init__()
        self.status = status

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
        raise RuntimeError(
            "raw failure api_key=sk-test-secret-abcdefghijklmnop\ntraceback leaked"
        )

    def get_run_status(self, session_id: str):
        return self.status


class ApiAppTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self):
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            client = TestClient(create_app())

            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "database": "not_configured"},
        )

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

    def test_research_stream_emits_safe_failure_terminal_event_after_runtime_error(self):
        runtime = FailingRuntime(
            {
                "session_id": "failed-api-session",
                "status": "failed",
                "phase": "planning",
                "iteration": 0,
                "error": "研究规划失败：三次均未通过大纲校验",
            }
        )
        client = TestClient(create_app(runtime=runtime))

        response = client.post(
            "/api/research/stream",
            json={"query": "东岳硅材近五年表现", "session_id": "failed-api-session"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("event: research_started\n", response.text)
        self.assertEqual(response.text.count("event: research_failed\n"), 1)
        terminal_frame = response.text.strip().split("\n\n")[-1]
        data_line = next(
            line.removeprefix("data: ")
            for line in terminal_frame.splitlines()
            if line.startswith("data: ")
        )
        terminal_data = json.loads(data_line)
        self.assertEqual(terminal_data["type"], "research_failed")
        self.assertEqual(terminal_data["session_id"], "failed-api-session")
        self.assertEqual(terminal_data["phase"], "planning")
        self.assertEqual(terminal_data["iteration"], 0)
        self.assertEqual(terminal_data["error"], "研究规划失败：三次均未通过大纲校验")
        self.assertNotIn("sk-test-secret", response.text)
        self.assertNotIn("traceback leaked", response.text)

    def test_research_stream_redacts_credentials_when_runtime_status_is_unavailable(self):
        runtime = FailingRuntime()
        client = TestClient(create_app(runtime=runtime))

        response = client.post(
            "/api/research/stream",
            json={"query": "测试规划失败", "session_id": "failed-no-status"},
        )

        terminal_frame = response.text.strip().split("\n\n")[-1]
        data_line = next(
            line.removeprefix("data: ")
            for line in terminal_frame.splitlines()
            if line.startswith("data: ")
        )
        terminal_data = json.loads(data_line)
        self.assertEqual(terminal_data["type"], "research_failed")
        self.assertIn("api_key=[REDACTED]", terminal_data["error"])
        self.assertNotIn("sk-test-secret-abcdefghijklmnop", response.text)
        self.assertNotIn("traceback leaked", response.text)

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
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            client = TestClient(create_app())

            response = client.get("/api/research/session/events")

        self.assertEqual(response.status_code, 503)

    def test_configured_database_url_automatically_wires_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "api.sqlite"
            database_url = f"sqlite:///{database_path}"
            engine = create_engine(database_url)
            Base.metadata.create_all(engine)
            engine.dispose()

            with patch.dict(os.environ, {"DATABASE_URL": database_url}):
                app = create_app()
                self.assertIsNotNone(app.state.repository)
                with TestClient(app) as client:
                    response = client.get("/health")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok", "database": "connected"})

    def test_stream_can_be_traced_after_recreating_api_app(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "trace.sqlite"
            database_url = f"sqlite:///{database_path}"
            engine = create_engine(database_url)
            Base.metadata.create_all(engine)
            engine.dispose()

            with patch.dict(
                os.environ,
                {
                    "DATABASE_URL": database_url,
                    "LLM_API_KEY": "",
                    "BOCHA_API_KEY": "",
                },
            ):
                with TestClient(create_app()) as client:
                    stream = client.post(
                        "/api/research/stream",
                        json={"query": "王维的一生", "session_id": "trace-session"},
                    )
                    self.assertEqual(stream.status_code, 200)
                    self.assertIn("event: research_completed", stream.text)

                with TestClient(create_app()) as restarted_client:
                    status = restarted_client.get("/api/research/trace-session/status")
                    events = restarted_client.get("/api/research/trace-session/events")
                    result = restarted_client.get("/api/research/trace-session/result")

            self.assertEqual(status.json()["status"], "completed")
            self.assertEqual(events.json()["events"][0]["type"], "research_started")
            self.assertEqual(events.json()["events"][-1]["type"], "research_completed")
            self.assertEqual(result.json()["query"], "王维的一生")
            self.assertTrue(result.json()["final_report"])

    def test_postgres_backed_endpoints_return_persisted_status_events_and_report(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        repository = ResearchRepository(
            sessionmaker(bind=engine, expire_on_commit=False),
            engine=engine,
        )
        state = ResearchState("王维的一生", session_id="saved-session")
        state.phase = "completed"
        state.final_report = "持久化的最终报告"
        state.planner_diagnostics = [
            {
                "agent": "planner",
                "attempt": 1,
                "model": "test-model",
                "accepted": True,
                "response_preview": '{"research_subject":"王维"}',
            }
        ]
        repository.save_state(state, status="completed")
        repository.append_event(
            {
                "type": "research_completed",
                "session_id": "saved-session",
                "phase": "completed",
                "iteration": 1,
                "report": state.final_report,
                "quality_score": 8.5,
                "references": [],
                "review_result": {},
                "critic_feedback": [],
                "unresolved_issues": [],
                "fact_check_results": [],
                "missing_aspects": [],
                "strengths": [],
                "insights": [],
                "data_points": [],
                "charts": [],
                "code_executions": [],
            }
        )

        try:
            with TestClient(create_app(repository=repository)) as client:
                status = client.get("/api/research/saved-session/status")
                events = client.get("/api/research/saved-session/events")
                result = client.get("/api/research/saved-session/result")

            self.assertEqual(status.status_code, 200)
            self.assertEqual(status.json()["status"], "completed")
            self.assertEqual(status.json()["iteration"], 1)
            self.assertEqual(events.status_code, 200)
            self.assertEqual(events.json()["events"][0]["sequence"], 0)
            self.assertIn("created_at", events.json()["events"][0])
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()["query"], "王维的一生")
            self.assertEqual(result.json()["final_report"], "持久化的最终报告")
            self.assertEqual(result.json()["quality_status"], "not_reviewed")
            self.assertFalse(result.json()["quality_gate_passed"])
            self.assertEqual(result.json()["planner_diagnostics"][0]["model"], "test-model")
        finally:
            engine.dispose()

    def test_planner_failure_returns_sse_terminal_frame_and_traceable_attempts(self):
        class InvalidPlannerClient(MockLLMClient):
            async def complete_json(self, role, payload, **kwargs):
                if role == "planner":
                    return {"outline": [], "research_questions": []}
                return await super().complete_json(role, payload, **kwargs)

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        repository = ResearchRepository(
            sessionmaker(bind=engine, expire_on_commit=False),
            engine=engine,
        )
        run_control = InMemoryRunControlStore()
        runtime = create_research_runtime(
            InvalidPlannerClient(),
            MockSearchClient(),
            repository=repository,
            run_control=run_control,
        )

        try:
            with TestClient(create_app(runtime=runtime)) as client:
                stream = client.post(
                    "/api/research/stream",
                    json={
                        "query": "介绍一下诗人王维的一生",
                        "session_id": "planner-failed-api",
                    },
                )
                status = client.get("/api/research/planner-failed-api/status")
                events = client.get("/api/research/planner-failed-api/events")
                result = client.get("/api/research/planner-failed-api/result")

            self.assertEqual(stream.status_code, 200)
            self.assertIn("event: research_failed\n", stream.text)
            self.assertIn("章节数为 0", stream.text)
            self.assertNotIn("response_preview", stream.text)
            self.assertEqual(status.json()["status"], "failed")
            self.assertEqual(status.json()["phase"], "planning")
            self.assertEqual(events.json()["events"][-1]["type"], "research_failed")
            self.assertEqual(
                len(events.json()["events"][-1]["planner_diagnostics"]), 3
            )
            self.assertEqual(len(result.json()["planner_diagnostics"]), 3)
            self.assertIn("章节数为 0", result.json()["planner_diagnostics"][0]["validation_error"])
        finally:
            engine.dispose()

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
