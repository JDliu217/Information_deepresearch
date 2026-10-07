import asyncio
import unittest
from types import SimpleNamespace

from app.core.bocha_search import BochaSearchClient, BochaSettings
from app.core.web_fetcher import WebPageFetcher, WebFetchSettings


class FakeResponse:
    def __init__(self, data=None, text="", status_code=200):
        self._data = data
        self.text = text
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("http error")


class FakeSearchHttpClient:
    def __init__(self):
        self.requests = []

    async def post(self, url, **kwargs):
        self.requests.append((url, kwargs))
        return FakeResponse(
            {
                "code": 200,
                "data": {
                    "webPages": {
                        "value": [
                            {
                                "name": "官方来源",
                                "url": "https://example.com/a",
                                "snippet": "摘要 A",
                                "summary": "摘要 A",
                            },
                            {
                                "name": "官方来源",
                                "url": "https://example.com/a",
                                "snippet": "重复结果",
                            },
                        ]
                    }
                },
            }
        )


class FakeFetcher:
    def __init__(self):
        self.urls = []

    async def fetch(self, url):
        self.urls.append(url)
        return "网页正文 A"


class WebSearchTests(unittest.TestCase):
    def test_web_page_fetcher_extracts_readable_text_and_ignores_script(self):
        class Http:
            async def get(self, url, **kwargs):
                return FakeResponse(text="<html><script>bad()</script><main><h1>标题</h1><p>正文内容</p></main></html>")

        result = asyncio.run(
            WebPageFetcher(WebFetchSettings(max_chars=1000), client=Http()).fetch("https://example.com")
        )

        self.assertIn("标题", result)
        self.assertIn("正文内容", result)
        self.assertNotIn("bad", result)

    def test_bocha_normalizes_deduplicates_and_fetches_content(self):
        http = FakeSearchHttpClient()
        fetcher = FakeFetcher()
        client = BochaSearchClient(
            BochaSettings(api_key="test-key", fetch_content=True),
            client=http,
            fetcher=fetcher,
        )

        results = asyncio.run(client.search("新能源汽车趋势", limit=3))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "官方来源")
        self.assertEqual(results[0].content, "网页正文 A")
        self.assertEqual(fetcher.urls, ["https://example.com/a"])
        self.assertEqual(http.requests[0][1]["json"]["count"], 3)
        self.assertEqual(http.requests[0][1]["headers"]["Authorization"], "Bearer test-key")

    def test_bocha_cache_avoids_duplicate_request(self):
        http = FakeSearchHttpClient()
        client = BochaSearchClient(
            BochaSettings(api_key="test-key", fetch_content=False), client=http
        )

        asyncio.run(client.search("缓存查询"))
        asyncio.run(client.search("缓存查询"))

        self.assertEqual(len(http.requests), 1)

    def test_bocha_requires_api_key(self):
        with self.assertRaises(ValueError):
            BochaSearchClient(BochaSettings(api_key=""))

    def test_bocha_does_not_fetch_full_pages_by_default(self):
        self.assertFalse(BochaSettings(api_key="test-key").fetch_content)


if __name__ == "__main__":
    unittest.main()
