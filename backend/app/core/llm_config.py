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


@dataclass(frozen=True)
class LLMSettings:
    """OpenAI 兼容服务配置；密钥只从环境变量读取。"""

    api_key: str = ""
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    default_model: str = "deepseek-v3.2"
    timeout_seconds: float = 90.0
    max_retries: int = 2
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
            ),
            "fact_extractor": AgentModelSettings(
                model=os.getenv("LLM_FACT_MODEL", default_model),
                temperature=0.15,
                max_tokens=16000,
            ),
            "data_analyst": AgentModelSettings(
                model=os.getenv("LLM_ANALYST_MODEL", default_model),
                temperature=0.2,
                max_tokens=9000,
            ),
            "code_wizard": AgentModelSettings(
                model=os.getenv("LLM_WIZARD_MODEL", default_model),
                temperature=0.15,
                max_tokens=7000,
            ),
            "writer": AgentModelSettings(
                model=os.getenv("LLM_WRITER_MODEL", default_model),
                temperature=0.55,
                max_tokens=16000,
            ),
            "critic": AgentModelSettings(
                model=os.getenv("LLM_CRITIC_MODEL", default_model),
                temperature=0.15,
                max_tokens=7000,
            ),
        }
        return cls(
            api_key=os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY", ""),
            base_url=os.getenv(
                "LLM_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ).rstrip("/"),
            default_model=default_model,
            timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "90")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
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

    def validate(self) -> None:
        if not self.api_key.strip():
            raise ValueError("缺少 LLM_API_KEY 或 DASHSCOPE_API_KEY")
        if not self.base_url.strip():
            raise ValueError("LLM_BASE_URL 不能为空")
        if self.timeout_seconds <= 0:
            raise ValueError("LLM_TIMEOUT_SECONDS 必须大于 0")
        if self.max_retries < 0:
            raise ValueError("LLM_MAX_RETRIES 不能小于 0")


__all__ = ["AgentModelSettings", "LLMSettings"]
