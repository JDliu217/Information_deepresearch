"""统一的搜索客户端接口。

搜索客户端只负责获取候选来源。
它不负责判断来源是否可信，也不负责把来源写成研究报告。
这些职责会交给后面的 Researcher 和 Writer。
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SearchResult:
    """一条搜索结果的统一格式。"""

    title: str
    url: str
    snippet: str
    query: str
    content: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换成适合放进 ResearchState 的字典。"""
        return asdict(self)


class SearchClient(ABC):
    """所有搜索服务都要遵守的接口。"""

    @abstractmethod
    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """根据一个研究子问题返回候选来源。"""
        raise NotImplementedError


class MockSearchClient(SearchClient):
    """本地模拟搜索服务。

    URL 使用查询内容的摘要生成，因此同一个查询每次都会得到同一个来源。
    这样测试不会依赖网络，也方便观察数据流。
    """

    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise ValueError("搜索问题不能为空")
        if limit < 1:
            raise ValueError("limit 必须大于 0")

        digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
        result = SearchResult(
            title=f"公开资料：{query}",
            url=f"https://example.com/research/{digest}",
            snippet=f"这是针对“{query}”的模拟公开资料摘要，用于验证研究流程。",
            query=query,
            content=f"模拟资料正文：{query}需要结合公开数据、行业实践和政策环境综合判断。",
        )
        return [result]
