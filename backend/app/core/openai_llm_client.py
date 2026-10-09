"""OpenAI 兼容协议的真实 LLM 客户端。"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from urllib.parse import urlparse

from .llm_client import LLMClient
from .llm_config import LLMSettings


class LLMInvocationError(RuntimeError):
    """真实 LLM 请求失败时提供可诊断、已脱敏的错误。"""

    def __init__(
        self,
        *,
        role: str,
        model: str,
        category: str,
        attempts: int,
        detail: str,
        response_preview: str = "",
    ) -> None:
        self.role = role
        self.model = model
        self.category = category
        self.attempts = attempts
        self.detail = detail
        self.response_preview = response_preview
        super().__init__(
            "真实 LLM 调用失败: "
            f"role={role}, model={model}, category={category}, "
            f"attempts={attempts}, detail={detail}"
        )


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
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        content = await self._complete(
            role,
            payload,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        parsed = self._parse_json(content)
        if not isinstance(parsed, dict):
            raise ValueError(f"真实 LLM 的 {role} 返回结果必须是 JSON 对象")
        return parsed

    async def complete_json_with_raw(
        self,
        role: str,
        payload: dict[str, Any],
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[dict[str, Any], str]:
        """Return the parsed object and exact response text for agent diagnostics."""

        content = await self._complete(
            role,
            payload,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        parsed = self._parse_json(content)
        if not isinstance(parsed, dict):
            raise ValueError(f"真实 LLM 的 {role} 返回结果必须是 JSON 对象")
        return parsed, content

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
        system_prompt: str = "",
        user_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        return await self._complete(
            role,
            payload,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=json_mode,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def _complete(
        self,
        role: str,
        payload: dict[str, Any],
        *,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        model_settings = self.settings.for_agent(role)
        # Prompt selection belongs to each Agent. Empty prompts remain accepted
        # for low-level compatibility; production Agent calls always provide both.
        if not user_prompt.strip():
            user_prompt = json.dumps(payload, ensure_ascii=False, default=str)
        if json_mode and not re.search(r"\bjson\b", f"{system_prompt}\n{user_prompt}", re.I):
            # DeepSeek requires the word JSON somewhere in the prompt when
            # response_format=json_object is used. This is a transport hint;
            # the Agent still owns the actual output schema and instructions.
            user_prompt = f"{user_prompt.rstrip()}\n\n请仅返回有效的 JSON 对象。"
        request: dict[str, Any] = {
            "model": model_settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": (
                model_settings.temperature if temperature is None else temperature
            ),
            "max_tokens": model_settings.max_tokens if max_tokens is None else max_tokens,
        }
        if self._uses_deepseek(self.settings.base_url):
            thinking = self.settings.thinking_for(role)
            request["extra_body"] = {"thinking": {"type": thinking}}
            if thinking == "enabled":
                reasoning_effort = self.settings.reasoning_effort_for(role)
                if reasoning_effort != "none":
                    request["reasoning_effort"] = reasoning_effort
        if json_mode:
            request["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        last_response_preview = ""
        attempts = 0
        for attempt in range(self.settings.max_retries + 1):
            attempts = attempt + 1
            try:
                response = await self._get_client().chat.completions.create(**request)
                content = self._response_content(response)
                last_response_preview = content[:12000]
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
        assert last_error is not None
        raise LLMInvocationError(
            role=role,
            model=model_settings.model,
            category=self._classify_error(last_error),
            attempts=attempts,
            detail=self._safe_error_detail(last_error),
            response_preview=self._redact_secrets(last_response_preview),
        ) from last_error

    @staticmethod
    def _uses_deepseek(base_url: str) -> bool:
        """Provider-specific fields belong only on the DeepSeek API endpoint."""

        hostname = (urlparse(base_url).hostname or "").lower()
        return hostname == "deepseek.com" or hostname.endswith(".deepseek.com")

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
    def _classify_error(error: Exception) -> str:
        """把常见服务商错误归类，便于定位配置或请求问题。"""

        status_code = getattr(error, "status_code", None)
        if isinstance(status_code, int):
            if status_code == 429:
                return "rate_limit"
            if 400 <= status_code < 500:
                return "provider_4xx"
            if status_code >= 500:
                return "provider_5xx"

        error_name = type(error).__name__.lower()
        error_text = str(error).lower()
        if "timeout" in error_name or "timeout" in error_text:
            return "timeout"
        if "connection" in error_name or "connect" in error_text:
            return "connection"
        if isinstance(error, ValueError):
            if "json" in error_text:
                return "invalid_json"
            return "invalid_response"
        return "unknown"

    def _safe_error_detail(self, error: Exception) -> str:
        """提取短错误摘要，避免把密钥或大段响应写入运行状态。"""

        detail = ""
        body = getattr(error, "body", None)
        if isinstance(body, dict):
            provider_error = body.get("error", body)
            if isinstance(provider_error, dict):
                detail = str(
                    provider_error.get("message")
                    or provider_error.get("code")
                    or provider_error.get("type")
                    or ""
                )
            elif provider_error:
                detail = str(provider_error)
        if not detail:
            detail = str(error).strip() or type(error).__name__

        status_code = getattr(error, "status_code", None)
        if isinstance(status_code, int):
            detail = f"http_status={status_code}; {detail}"
        detail = self._redact_secrets(detail)
        detail = " ".join(detail.split())
        return detail[:500]

    def _redact_secrets(self, value: str) -> str:
        """Remove configured and common token-shaped credentials from traces."""

        if self.settings.api_key:
            value = value.replace(self.settings.api_key, "[redacted-api-key]")
        value = re.sub(
            r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+",
            r"\1[redacted-token]",
            value,
        )
        value = re.sub(
            r"(?i)(api[_-]?key[\"']?\s*[=:]\s*[\"']?)[^\s,\"'}]+",
            r"\1[redacted-api-key]",
            value,
        )
        value = re.sub(
            r"(?i)((?:access[_-]?token|refresh[_-]?token|password|secret|authorization)"
            r"[\"']?\s*[=:]\s*[\"']?)[^\s,\"'}]+",
            r"\1[redacted-secret]",
            value,
        )
        value = re.sub(r"\bsk-[A-Za-z0-9_-]{8,}\b", "[redacted-token]", value)
        return value

    @staticmethod
    def _response_content(response: Any) -> str:
        choices = getattr(response, "choices", None)
        if not choices:
            raise ValueError("LLM 响应缺少 choices")
        choice = choices[0]
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, list):
            content = "".join(
                str(item.get("text", "")) if isinstance(item, dict) else str(item)
                for item in content
            )
        finish_reason = getattr(choice, "finish_reason", None)
        reasoning_content = getattr(message, "reasoning_content", None)
        reasoning_chars = len(reasoning_content) if isinstance(reasoning_content, str) else 0
        refusal = getattr(message, "refusal", None)
        if not isinstance(content, str) or not content.strip():
            detail = (
                "LLM 响应 content 为空或无效; "
                f"finish_reason={finish_reason!r}; "
                f"reasoning_chars={reasoning_chars}; "
                f"refusal={str(refusal)[:120]!r}"
            )
            raise ValueError(detail)
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


__all__ = ["LLMInvocationError", "OpenAICompatibleLLMClient"]
