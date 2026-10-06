import asyncio
import unittest

from app.core.search_client import MockSearchClient, SearchClient, SearchResult


class SearchClientTests(unittest.TestCase):
    def test_mock_client_implements_search_interface(self):
        self.assertIsInstance(MockSearchClient(), SearchClient)

    def test_search_returns_normalized_result(self):
        client = MockSearchClient()

        results = asyncio.run(client.search("新能源汽车行业的市场规模是什么？"))

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], SearchResult)
        self.assertTrue(results[0].title)
        self.assertTrue(results[0].url.startswith("https://"))
        self.assertTrue(results[0].snippet)
        self.assertEqual(results[0].query, "新能源汽车行业的市场规模是什么？")

    def test_same_query_has_stable_url(self):
        client = MockSearchClient()

        first = asyncio.run(client.search("稳定查询"))[0]
        second = asyncio.run(client.search("稳定查询"))[0]

        self.assertEqual(first.url, second.url)

    def test_search_rejects_invalid_input(self):
        client = MockSearchClient()

        with self.assertRaises(ValueError):
            asyncio.run(client.search("   "))
        with self.assertRaises(ValueError):
            asyncio.run(client.search("测试", limit=0))


if __name__ == "__main__":
    unittest.main()
