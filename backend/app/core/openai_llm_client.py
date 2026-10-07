"""OpenAI 兼容协议的真实 LLM 客户端。"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from app.prompts import build_prompt

from .llm_client import LLMClient
from .llm_config import LLMSettings


class OpenAICompatibleLLMClient(LLMClient):
    """调用 DashScope、DeepSeek、OpenAI 等 OpenAI 兼容服务。"""

    def __init__(self, settings: LLMSettings | None = None, *, client: Any | None = None):
        self.settings = settings or LLMSettings.from_env()
        if client is not None:
            self.client = client
        else:
            self.settings.validate()
            self.client = None

    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        content = await self._complete(role, payload, json_mode=True)
        parsed = self._parse_json(content)
        if not isinstance(parsed, dict):
            raise ValueError(f"真实 LLM 的 {role} 返回结果必须是 JSON 对象")
        return parsed

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        content = await self._complete(role, payload, json_mode=False)
        parsed = self._try_parse_json(content)
        if isinstance(parsed, dict):
            mode = payload.get("mode")
            output_field = {
                "section": "content",
                "report": "full_report",
                "revision": "revised_content",
            }.get(str(mode))
            if output_field and isinstance(parsed.get(output_field), str):
                return parsed[output_field].strip()
        return content.strip()

    async def _complete(
        self,
        role: str,
        payload: dict[str, Any],
        *,
        json_mode: bool,
    ) -> str:
        system_prompt, user_prompt = build_prompt(role, payload)
        model_settings = self.settings.for_agent(role)
        request: dict[str, Any] = {
            "model": model_settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": model_settings.temperature,
            "max_tokens": model_settings.max_tokens,
        }
        if json_mode:
            request["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                response = await self._get_client().chat.completions.create(**request)
                content = self._response_content(response)
                if not content:
                    raise ValueError(f"真实 LLM 的 {role} 返回空内容")
                if json_mode:
                    self._parse_json(content)
                return content
            except Exception as exc:
                last_error = exc
                if attempt >= self.settings.max_retries:
                    break
                await asyncio.sleep(min(2**attempt, 4))
        raise RuntimeError(f"真实 LLM 调用失败: role={role}") from last_error

    def _get_client(self) -> Any:
        if self.client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:
                raise RuntimeError("使用真实 LLM 前请安装 openai 依赖") from exc
            self.client = AsyncOpenAI(
                api_key=self.settings.api_key,
                base_url=self.settings.base_url,
                timeout=self.settings.timeout_seconds,
                max_retries=0,
            )
        return self.client

    @staticmethod
    def _response_content(response: Any) -> str:
        choices = getattr(response, "choices", None)
        if not choices:
            raise ValueError("LLM 响应缺少 choices")
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, list):
            content = "".join(
                str(item.get("text", "")) if isinstance(item, dict) else str(item)
                for item in content
            )
        if not isinstance(content, str):
            raise ValueError("LLM 响应缺少文本 content")
        return content.strip()

    @classmethod
    def _parse_json(cls, content: str) -> Any:
        parsed = cls._try_parse_json(content)
        if parsed is None:
            raise ValueError("真实 LLM 返回的内容不是有效 JSON")
        return parsed

    @staticmethod
    def _try_parse_json(content: str) -> Any | None:
        text = content.strip().lstrip("\ufeff")
        candidates = [text]
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            candidates.append(match.group(1).strip())
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            candidates.append(text[start : end + 1])
        for candidate in candidates:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        return None


__all__ = ["OpenAICompatibleLLMClient"]
