"""网页正文抓取和基础清洗。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any


@dataclass(frozen=True)
class WebFetchSettings:
    timeout_seconds: float = 20.0
    max_chars: int = 20_000
    user_agent: str = "InformationDeepResearch/2.0"


class _ReadableTextParser(HTMLParser):
    """去除脚本、样式和导航区域的轻量正文解析器。"""

    _ignored_tags = {"script", "style", "noscript", "template", "svg", "canvas"}
    _section_breaks = {"article", "main", "section", "p", "div", "li", "br", "h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._ignored_tags:
            self._ignored_depth += 1
        if tag in self._section_breaks and self._ignored_depth == 0:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._section_breaks and self._ignored_depth == 0:
            self.parts.append("\n")
        if tag in self._ignored_tags and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth == 0:
            self.parts.append(data)

    def text(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        return text.strip()


class WebPageFetcher:
    """抓取网页正文；HTTP 客户端可注入以便测试。"""

    def __init__(
        self,
        settings: WebFetchSettings | None = None,
        *,
        client: Any | None = None,
    ) -> None:
        self.settings = settings or WebFetchSettings()
        if self.settings.timeout_seconds <= 0:
            raise ValueError("网页抓取 timeout_seconds 必须大于 0")
        if self.settings.max_chars < 100:
            raise ValueError("网页抓取 max_chars 不能小于 100")
        self.client = client

    async def fetch(self, url: str) -> str:
        """返回清洗后的正文；失败时返回空字符串。"""

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("网页 URL 必须使用 http 或 https")
        response = await self._get_client().get(
            url,
            headers={"User-Agent": self.settings.user_agent},
            timeout=self.settings.timeout_seconds,
        )
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        html = response.text
        parser = _ReadableTextParser()
        parser.feed(html)
        parser.close()
        return parser.text()[: self.settings.max_chars]

    def _get_client(self) -> Any:
        if self.client is None:
            try:
                import httpx
            except ImportError as exc:
                raise RuntimeError("网页抓取需要安装 httpx") from exc
            self.client = httpx.AsyncClient(follow_redirects=True)
        return self.client


__all__ = ["WebFetchSettings", "WebPageFetcher"]
