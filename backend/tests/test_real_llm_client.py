import asyncio
import os
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from app.core import env as env_module
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

    def test_settings_read_global_and_role_thinking_configuration(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(
                os.environ,
                {
                    "LLM_API_KEY": "test-key",
                    "LLM_MODEL": "deepseek-chat",
                    "LLM_THINKING": "enabled",
                    "LLM_REASONING_EFFORT": "medium",
                    "LLM_FACT_THINKING": "disabled",
                },
                clear=True,
            ):
                settings = LLMSettings.from_env()

        self.assertEqual(settings.thinking, "enabled")
        self.assertEqual(settings.reasoning_effort, "medium")
        self.assertEqual(settings.thinking_for("planner"), "enabled")
        self.assertEqual(settings.reasoning_effort_for("planner"), "medium")
        self.assertEqual(settings.thinking_for("fact_extractor"), "disabled")
        self.assertEqual(settings.reasoning_effort_for("fact_extractor"), "medium")

    def test_complete_json_sends_high_quality_structured_prompt(self):
        fake = FakeClient(['{"outline": [], "research_questions": [], "hypotheses": [], "key_entities": []}'])
        client = OpenAICompatibleLLMClient(self.settings(), client=fake)

        result = asyncio.run(
            client.complete_json(
                "planner",
                {"query": "新能源汽车"},
                system_prompt="你是研究规划 Agent，必须输出假设。",
                user_prompt='请返回包含 search_queries 的 JSON。',
            )
        )

        request = fake.chat.completions.requests[0]
        self.assertEqual(result["outline"], [])
        self.assertEqual(request["model"], "test-model")
        self.assertEqual(request["response_format"], {"type": "json_object"})
        self.assertIn("假设", request["messages"][0]["content"])
        self.assertIn("search_queries", request["messages"][1]["content"])

    def test_deepseek_thinking_disabled_does_not_send_reasoning_effort(self):
        fake = FakeClient(['{"outline": []}'])
        settings = self.settings(
            base_url="https://api.deepseek.com",
            thinking="disabled",
            reasoning_effort="high",
        )
        client = OpenAICompatibleLLMClient(settings, client=fake)

        asyncio.run(client.complete_json("planner", {"query": "测试"}))

        request = fake.chat.completions.requests[0]
        self.assertEqual(request["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertNotIn("reasoning_effort", request)

    def test_deepseek_thinking_enabled_sends_configured_reasoning_effort(self):
        fake = FakeClient(['{"outline": []}'])
        settings = self.settings(
            base_url="https://api.deepseek.com",
            thinking="enabled",
            reasoning_effort="low",
        )
        client = OpenAICompatibleLLMClient(settings, client=fake)

        asyncio.run(client.complete_json("planner", {"query": "测试"}))

        request = fake.chat.completions.requests[0]
        self.assertEqual(request["extra_body"], {"thinking": {"type": "enabled"}})
        self.assertEqual(request["reasoning_effort"], "low")

    def test_non_deepseek_provider_does_not_receive_deepseek_parameters(self):
        fake = FakeClient(['{"outline": []}'])
        settings = self.settings(
            base_url="https://api.openai.com/v1",
            thinking="enabled",
            reasoning_effort="high",
        )
        client = OpenAICompatibleLLMClient(settings, client=fake)

        asyncio.run(client.complete_json("planner", {"query": "测试"}))

        request = fake.chat.completions.requests[0]
        self.assertNotIn("extra_body", request)
        self.assertNotIn("reasoning_effort", request)

    def test_deepseek_model_on_dashscope_does_not_receive_deepseek_parameters(self):
        fake = FakeClient(['{"outline": []}'])
        settings = self.settings(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            thinking="disabled",
            agents={"planner": AgentModelSettings("deepseek-v3.2", 0.2, 1000)},
        )
        client = OpenAICompatibleLLMClient(settings, client=fake)

        asyncio.run(client.complete_json("planner", {"query": "测试"}))

        request = fake.chat.completions.requests[0]
        self.assertNotIn("extra_body", request)
        self.assertNotIn("reasoning_effort", request)

    def test_complete_text_returns_raw_response_for_agent_to_parse(self):
        fake = FakeClient(['{"full_report": "## 执行摘要\\n内容", "references": []}'])
        client = OpenAICompatibleLLMClient(self.settings(), client=fake)

        result = asyncio.run(
            client.complete_text("writer", {"mode": "report", "query": "测试"})
        )

        self.assertEqual(result, '{"full_report": "## 执行摘要\\n内容", "references": []}')
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
