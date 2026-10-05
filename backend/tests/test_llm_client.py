import asyncio
import unittest

from app.core.llm_client import LLMClient, MockLLMClient


class LLMClientTests(unittest.TestCase):
    def test_mock_client_implements_llm_interface(self):
        self.assertIsInstance(MockLLMClient(), LLMClient)

    def test_mock_planner_returns_structured_result(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "planner",
                {"query": "新能源汽车行业的发展趋势是什么？"},
            )
        )

        self.assertEqual(len(result["plan"]), 3)
        self.assertEqual(len(result["research_questions"]), 3)
        self.assertIn("新能源汽车", result["research_questions"][0])

    def test_mock_client_rejects_unknown_role(self):
        client = MockLLMClient()

        with self.assertRaises(ValueError):
            asyncio.run(client.complete_json("unknown", {"query": "测试"}))

    def test_mock_writer_returns_text(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_text("writer", {"query": "测试行业"})
        )

        self.assertIn("测试行业", result)


if __name__ == "__main__":
    unittest.main()
