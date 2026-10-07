import asyncio
import unittest
from types import SimpleNamespace

from app.core.llm_config import AgentModelSettings, LLMSettings
from app.core.openai_llm_client import OpenAICompatibleLLMClient


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


class RealLLMClientTests(unittest.TestCase):
    def settings(self, **kwargs):
        agents = {
            "planner": AgentModelSettings("test-model", 0.2, 1000),
            "writer": AgentModelSettings("writer-model", 0.6, 2000),
        }
        return LLMSettings(api_key="test-key", agents=agents, **kwargs)

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

        with self.assertRaises(RuntimeError):
            asyncio.run(client.complete_json("planner", {"query": "测试"}))

        self.assertEqual(len(fake.chat.completions.requests), 2)


if __name__ == "__main__":
    unittest.main()
