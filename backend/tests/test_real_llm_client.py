import asyncio
import unittest
from types import SimpleNamespace

from app.core.llm_config import AgentModelSettings, LLMSettings
from app.core.openai_llm_client import LLMInvocationError, OpenAICompatibleLLMClient


class FakeCompletions:
    def __init__(self, contents):
        self.contents = iter(contents)
        self.requests = []

    async def create(self, **request):
        self.requests.append(request)
        content = next(self.contents)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class FakeClient:
    def __init__(self, contents):
        self.chat = SimpleNamespace(completions=FakeCompletions(contents))


class FailingCompletions:
    def __init__(self, error):
        self.error = error
        self.requests = []

    async def create(self, **request):
        self.requests.append(request)
        raise self.error


class FailingClient:
    def __init__(self, error):
        self.chat = SimpleNamespace(completions=FailingCompletions(error))


class EmptyResponseCompletions:
    async def create(self, **request):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="length",
                    message=SimpleNamespace(
                        content="",
                        reasoning_content="思考过程" * 10,
                        refusal=None,
                    ),
                )
            ]
        )


class EmptyResponseClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=EmptyResponseCompletions())


class ProviderError(Exception):
    status_code = 400

    def __init__(self, message, body):
        super().__init__(message)
        self.body = body


class RealLLMClientTests(unittest.TestCase):
    def settings(self, **kwargs):
        agents = {
            "planner": AgentModelSettings("test-model", 0.2, 1000),
            "writer": AgentModelSettings("writer-model", 0.6, 2000),
        }
        values = {"api_key": "test-key", "agents": agents}
        values.update(kwargs)
        return LLMSettings(**values)

    def test_complete_json_sends_high_quality_structured_prompt(self):
        fake = FakeClient(['{"outline": [], "research_questions": [], "hypotheses": [], "key_entities": []}'])
        client = OpenAICompatibleLLMClient(self.settings(), client=fake)

        result = asyncio.run(client.complete_json("planner", {"query": "新能源汽车"}))

        request = fake.chat.completions.requests[0]
        self.assertEqual(result["outline"], [])
        self.assertEqual(request["model"], "test-model")
        self.assertEqual(request["response_format"], {"type": "json_object"})
        self.assertIn("假设", request["messages"][0]["content"])
        self.assertIn("search_queries", request["messages"][1]["content"])

    def test_complete_text_extracts_report_field_from_json_response(self):
        fake = FakeClient(['{"full_report": "## 执行摘要\\n内容", "references": []}'])
        client = OpenAICompatibleLLMClient(self.settings(), client=fake)

        result = asyncio.run(
            client.complete_text("writer", {"mode": "report", "query": "测试"})
        )

        self.assertEqual(result, "## 执行摘要\n内容")
        self.assertNotIn("response_format", fake.chat.completions.requests[0])

    def test_invalid_json_is_retried_and_then_reported(self):
        fake = FakeClient(["不是 JSON", "仍然不是 JSON"])
        settings = self.settings(max_retries=1)
        client = OpenAICompatibleLLMClient(settings, client=fake)

        with self.assertRaises(LLMInvocationError) as context:
            asyncio.run(client.complete_json("planner", {"query": "测试"}))

        self.assertEqual(len(fake.chat.completions.requests), 2)
        self.assertEqual(context.exception.category, "invalid_json")
        self.assertEqual(context.exception.attempts, 2)
        self.assertIn("真实 LLM 调用失败", str(context.exception))

    def test_provider_error_keeps_status_and_redacts_api_key(self):
        error = ProviderError(
            "provider rejected sk-secret-key",
            {"error": {"message": "response_format is not supported"}},
        )
        fake = FailingClient(error)
        settings = self.settings(api_key="sk-secret-key", max_retries=0)
        client = OpenAICompatibleLLMClient(settings, client=fake)

        with self.assertRaises(LLMInvocationError) as context:
            asyncio.run(client.complete_json("planner", {"query": "测试"}))

        self.assertEqual(context.exception.category, "provider_4xx")
        self.assertIn("http_status=400", str(context.exception))
        self.assertIn("response_format is not supported", str(context.exception))
        self.assertNotIn("sk-secret-key", str(context.exception))

    def test_empty_response_reports_finish_reason_and_reasoning_size(self):
        client = OpenAICompatibleLLMClient(
            self.settings(max_retries=0),
            client=EmptyResponseClient(),
        )

        with self.assertRaises(LLMInvocationError) as context:
            asyncio.run(client.complete_json("planner", {"query": "测试"}))

        self.assertEqual(context.exception.category, "invalid_response")
        self.assertIn("finish_reason='length'", str(context.exception))
        self.assertIn("reasoning_chars=40", str(context.exception))


if __name__ == "__main__":
    unittest.main()
