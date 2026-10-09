"""根据环境变量组装 Mock 或真实服务客户端。"""

from __future__ import annotations

import os
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from app.graph.runtime import ResearchGraphRuntime, create_research_runtime
from app.persistence.database import (
    DatabaseSettings,
    create_database_engine,
    create_session_factory,
)
from app.persistence.repository import ResearchRepository

from .env import load_project_env
from .llm_client import MockLLMClient
from .llm_config import LLMSettings
from .openai_llm_client import OpenAICompatibleLLMClient
from .run_control import InMemoryRunControlStore, RunControlStore
from .search_client import MockSearchClient, SearchClient


def create_configured_llm(*, force_real: bool = False):
    """有 API Key 时创建真实客户端，否则回退到 Mock。"""

    settings = LLMSettings.from_env()
    has_key = bool(settings.api_key.strip())
    if force_real or has_key:
        return OpenAICompatibleLLMClient(settings)
    return MockLLMClient()


def create_configured_search(*, force_real: bool = False) -> SearchClient:
    """有 Bocha Key 时创建真实搜索客户端，否则回退到 Mock。"""

    load_project_env()
    has_key = bool(os.getenv("BOCHA_API_KEY", "").strip())
    if force_real or has_key:
        from .bocha_search import BochaSearchClient

        return BochaSearchClient()
    return MockSearchClient()


def create_configured_runtime(
    *,
    run_control: RunControlStore | None = None,
    repository: ResearchRepository | None = None,
    checkpointer: Any | None = None,
    force_real: bool = False,
) -> ResearchGraphRuntime:
    """按环境配置创建完整 runtime。"""

    load_project_env()
    try:
        max_iterations = int(os.getenv("RESEARCH_MAX_ITERATIONS", "3"))
    except ValueError as exc:
        raise ValueError("RESEARCH_MAX_ITERATIONS 必须是非负整数") from exc
    if max_iterations < 0:
        raise ValueError("RESEARCH_MAX_ITERATIONS 必须是非负整数")

    control = run_control or InMemoryRunControlStore()
    if repository is None:
        database_settings = DatabaseSettings.from_env()
        if database_settings.url:
            engine = create_database_engine(database_settings)
            repository = ResearchRepository(
                create_session_factory(engine),
                engine=engine,
                owns_engine=True,
            )
    saver = checkpointer or InMemorySaver(
        serde=JsonPlusSerializer(
            allowed_msgpack_modules=[("app.domain.state", "ResearchState")]
        )
    )
    return create_research_runtime(
        create_configured_llm(force_real=force_real),
        create_configured_search(force_real=force_real),
        max_iterations=max_iterations,
        run_control=control,
        repository=repository,
        checkpointer=saver,
    )


__all__ = ["create_configured_llm", "create_configured_runtime", "create_configured_search"]
