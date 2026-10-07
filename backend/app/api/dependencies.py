"""FastAPI 依赖注入。

默认实例只使用 Mock 客户端和内存运行控制，便于本地学习和 API 测试；部署时
调用方可以把真实 runtime 注入 ``create_app``。
"""

from __future__ import annotations

from fastapi import Request
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from app.core.run_control import InMemoryRunControlStore, RunControlStore
from app.graph.runtime import ResearchGraphRuntime, create_research_runtime
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.persistence.repository import ResearchRepository


def build_default_runtime(
    run_control: RunControlStore | None = None,
    repository: ResearchRepository | None = None,
    checkpointer=None,
) -> ResearchGraphRuntime:
    """建立不依赖外部服务的默认 runtime。"""

    control = run_control or InMemoryRunControlStore()
    saver = checkpointer or InMemorySaver(
        serde=JsonPlusSerializer(
            allowed_msgpack_modules=[("app.domain.state", "ResearchState")]
        )
    )
    return create_research_runtime(
        MockLLMClient(),
        MockSearchClient(),
        run_control=control,
        repository=repository,
        checkpointer=saver,
    )


def get_runtime(request: Request) -> ResearchGraphRuntime:
    """从应用状态获取 runtime。"""

    return request.app.state.research_runtime


def get_run_control(request: Request) -> RunControlStore | None:
    """从应用状态获取运行控制存储。"""

    return request.app.state.run_control


def get_repository(request: Request) -> ResearchRepository | None:
    """从应用状态获取 PostgreSQL Repository。"""

    return request.app.state.repository
