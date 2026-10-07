"""真实 LLM 客户端的环境配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .env import load_project_env


@dataclass(frozen=True)
class AgentModelSettings:
    """一个 Agent 的模型参数。"""

    model: str
    temperature: float
    max_tokens: int
    # None 表示沿用 LLMSettings 的全局值；保留默认值以兼容现有三参数构造。
    thinking: str | None = None
    reasoning_effort: str | None = None


@dataclass(frozen=True)
class LLMSettings:
    """OpenAI 兼容服务配置；密钥只从环境变量读取。"""

    api_key: str = ""
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    default_model: str = "deepseek-v3.2"
    timeout_seconds: float = 90.0
    max_retries: int = 2
    # DeepSeek thinking 默认关闭，避免推理内容耗尽结构化输出预算。
    thinking: str = "disabled"
    reasoning_effort: str = "none"
    agents: dict[str, AgentModelSettings] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "LLMSettings":
        """从环境变量构建配置，不打印或暴露密钥。"""

        load_project_env()
        default_model = os.getenv("LLM_MODEL", "deepseek-v3.2")
        agents = {
            "planner": AgentModelSettings(
                model=os.getenv("LLM_PLANNER_MODEL", default_model),
                temperature=0.35,
                max_tokens=5000,
                thinking=_optional_env("LLM_PLANNER_THINKING"),
                reasoning_effort=_optional_env("LLM_PLANNER_REASONING_EFFORT"),
            ),
            "fact_extractor": AgentModelSettings(
                model=os.getenv("LLM_FACT_MODEL", default_model),
                temperature=0.15,
                max_tokens=16000,
                thinking=_optional_env("LLM_FACT_THINKING"),
                reasoning_effort=_optional_env("LLM_FACT_REASONING_EFFORT"),
            ),
            "data_analyst": AgentModelSettings(
                model=os.getenv("LLM_ANALYST_MODEL", default_model),
                temperature=0.2,
                max_tokens=9000,
                thinking=_optional_env("LLM_ANALYST_THINKING"),
                reasoning_effort=_optional_env("LLM_ANALYST_REASONING_EFFORT"),
            ),
            "code_wizard": AgentModelSettings(
                model=os.getenv("LLM_WIZARD_MODEL", default_model),
                temperature=0.15,
                max_tokens=7000,
                thinking=_optional_env("LLM_WIZARD_THINKING"),
                reasoning_effort=_optional_env("LLM_WIZARD_REASONING_EFFORT"),
            ),
            "writer": AgentModelSettings(
                model=os.getenv("LLM_WRITER_MODEL", default_model),
                temperature=0.55,
                max_tokens=16000,
                thinking=_optional_env("LLM_WRITER_THINKING"),
                reasoning_effort=_optional_env("LLM_WRITER_REASONING_EFFORT"),
            ),
            "critic": AgentModelSettings(
                model=os.getenv("LLM_CRITIC_MODEL", default_model),
                temperature=0.15,
                max_tokens=7000,
                thinking=_optional_env("LLM_CRITIC_THINKING"),
                reasoning_effort=_optional_env("LLM_CRITIC_REASONING_EFFORT"),
            ),
        }
        thinking = _normalize_thinking(os.getenv("LLM_THINKING", "disabled"))
        reasoning_effort = _normalize_reasoning_effort(
            os.getenv("LLM_REASONING_EFFORT", "none")
        )
        return cls(
            api_key=os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY", ""),
            base_url=os.getenv(
                "LLM_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ).rstrip("/"),
            default_model=default_model,
            timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "90")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
            thinking=thinking,
            reasoning_effort=reasoning_effort,
            agents=agents,
        )

    def for_agent(self, role: str) -> AgentModelSettings:
        """获取 Agent 参数；未知角色回退到默认配置。"""

        return self.agents.get(
            role,
            AgentModelSettings(
                model=self.default_model,
                temperature=0.3,
                max_tokens=8000,
            ),
        )

    def thinking_for(self, role: str) -> str:
        """返回角色 thinking 配置；未覆盖时使用全局值。"""

        value = self.for_agent(role).thinking
        return _normalize_thinking(value if value is not None else self.thinking)

    def reasoning_effort_for(self, role: str) -> str:
        """返回角色推理强度；未覆盖时使用全局值。"""

        value = self.for_agent(role).reasoning_effort
        return _normalize_reasoning_effort(
            value if value is not None else self.reasoning_effort
        )

    def validate(self) -> None:
        if not self.api_key.strip():
            raise ValueError("缺少 LLM_API_KEY 或 DASHSCOPE_API_KEY")
        if not self.base_url.strip():
            raise ValueError("LLM_BASE_URL 不能为空")
        if self.timeout_seconds <= 0:
            raise ValueError("LLM_TIMEOUT_SECONDS 必须大于 0")
        if self.max_retries < 0:
            raise ValueError("LLM_MAX_RETRIES 不能小于 0")


def _optional_env(name: str) -> str | None:
    """读取可选的角色配置；空字符串视为未设置。"""

    value = os.getenv(name)
    return value.strip() or None if value is not None else None


def _normalize_thinking(value: str | None) -> str:
    """只接受服务商通用的 thinking 开关值，异常值回退为 disabled。"""

    normalized = str(value or "disabled").strip().lower()
    return normalized if normalized in {"enabled", "disabled"} else "disabled"


def _normalize_reasoning_effort(value: str | None) -> str:
    """标准化推理强度；none 表示不发送该可选参数。"""

    normalized = str(value or "none").strip().lower()
    return normalized if normalized in {"none", "low", "medium", "high"} else "none"


__all__ = ["AgentModelSettings", "LLMSettings"]
