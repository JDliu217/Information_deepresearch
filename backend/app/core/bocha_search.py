"""Bocha Web Search API 的 SearchClient 适配器。"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from .env import load_project_env
from .search_client import SearchClient, SearchResult
from .web_fetcher import WebPageFetcher, WebFetchSettings


@dataclass(frozen=True)
class BochaSettings:
    api_key: str = ""
    endpoint: str = "https://api.bocha.cn/v1/web-search"
    timeout_seconds: float = 30.0
    max_retries: int = 2
    freshness: str = "noLimit"
    fetch_content: bool = False
    max_content_chars: int = 20_000
    max_fetch_concurrency: int = 4

    @classmethod
    def from_env(cls) -> "BochaSettings":
        load_project_env()
        return cls(
            api_key=os.getenv("BOCHA_API_KEY", ""),
            endpoint=os.getenv("BOCHA_ENDPOINT", cls.endpoint),
            timeout_seconds=float(os.getenv("BOCHA_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.getenv("BOCHA_MAX_RETRIES", "2")),
            freshness=os.getenv("BOCHA_FRESHNESS", "noLimit"),
            fetch_content=os.getenv("BOCHA_FETCH_CONTENT", "0").lower()
            in {"1", "true", "yes"},
            max_content_chars=int(os.getenv("BOCHA_MAX_CONTENT_CHARS", "20000")),
            max_fetch_concurrency=int(os.getenv("BOCHA_FETCH_CONCURRENCY", "4")),
        )

    def validate(self) -> None:
        if not self.api_key.strip():
            raise ValueError("缺少 BOCHA_API_KEY")
        if not self.endpoint.strip():
            raise ValueError("BOCHA_ENDPOINT 不能为空")
        if self.timeout_seconds <= 0:
            raise ValueError("BOCHA_TIMEOUT_SECONDS 必须大于 0")
        if self.max_retries < 0:
            raise ValueError("BOCHA_MAX_RETRIES 不能小于 0")
        if self.max_fetch_concurrency < 1:
            raise ValueError("BOCHA_FETCH_CONCURRENCY 必须大于 0")


class BochaSearchClient(SearchClient):
    """将 Bocha 返回结果统一为项目内部的 SearchResult。"""

    def __init__(
        self,
        settings: BochaSettings | None = None,
        *,
        client: Any | None = None,
        fetcher: WebPageFetcher | None = None,
    ) -> None:
        self.settings = settings or BochaSettings.from_env()
        self.settings.validate()
        self.client = client
        self.fetcher = fetcher or WebPageFetcher(
            WebFetchSettings(
                timeout_seconds=min(self.settings.timeout_seconds, 20.0),
                max_chars=self.settings.max_content_chars,
            )
        )
        self._cache: dict[tuple[str, int], list[SearchResult]] = {}

    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise ValueError("搜索问题不能为空")
        if limit < 1:
            raise ValueError("limit 必须大于 0")
        cache_key = (query, limit)
        if cache_key in self._cache:
            return list(self._cache[cache_key])

        payload = {
            "query": query,
            "summary": True,
            "count": limit,
            "freshness": self.settings.freshness,
        }
        response_data = await self._request(payload)
        raw_results = (
            response_data.get("data", {}).get("webPages", {}).get("value", [])
            if isinstance(response_data, dict)
            else []
        )
        results = self._normalize_results(raw_results, query)
        if self.settings.fetch_content and results:
            await self._fetch_contents(results)
        self._cache[cache_key] = list(results)
        return results

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = {
            "headers": {
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
            "json": payload,
            "timeout": self.settings.timeout_seconds,
        }
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                response = await self._get_client().post(self.settings.endpoint, **request)
                status_code = getattr(response, "status_code", 200)
                if status_code != 200:
                    raise RuntimeError(f"Bocha HTTP 状态码: {status_code}")
                data = response.json()
                if data.get("code") not in (None, 200):
                    raise RuntimeError(f"Bocha API 错误: {data.get('msg', 'unknown')}")
                return data
            except Exception as exc:
                last_error = exc
                if attempt >= self.settings.max_retries:
                    break
                await asyncio.sleep(min(2**attempt, 4))
        raise RuntimeError("Bocha 搜索请求失败") from last_error

    @staticmethod
    def _normalize_results(raw_results: Any, query: str) -> list[SearchResult]:
        if not isinstance(raw_results, list):
            return []
        results: list[SearchResult] = []
        seen_urls: set[str] = set()
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url", "")).strip()
            summary = str(item.get("summary") or item.get("snippet") or "").strip()
            if not url or not summary or url in seen_urls:
                continue
            seen_urls.add(url)
            results.append(
                SearchResult(
                    title=str(item.get("name") or item.get("title") or "未命名来源").strip(),
                    url=url,
                    snippet=str(item.get("snippet") or summary).strip(),
                    query=query,
                    content=summary,
                )
            )
        return results

    async def _fetch_contents(self, results: list[SearchResult]) -> None:
        semaphore = asyncio.Semaphore(self.settings.max_fetch_concurrency)

        async def fetch_one(result: SearchResult) -> None:
            async with semaphore:
                try:
                    content = await self.fetcher.fetch(result.url)
                except Exception:
                    content = ""
                if content.strip():
                    result.content = content.strip()

        await asyncio.gather(*(fetch_one(result) for result in results))

    def _get_client(self) -> Any:
        if self.client is None:
            try:
                import httpx
            except ImportError as exc:
                raise RuntimeError("Bocha 搜索需要安装 httpx") from exc
            self.client = httpx.AsyncClient()
        return self.client


__all__ = ["BochaSearchClient", "BochaSettings"]
