"""FastAPI 依赖注入。

默认实例只使用 Mock 客户端和内存运行控制，便于本地学习和 API 测试；部署时
调用方可以把真实 runtime 注入 ``create_app``。
"""

from __future__ import annotations

from fastapi import Request

from app.core.run_control import InMemoryRunControlStore, RunControlStore
from app.graph.runtime import ResearchGraphRuntime, create_research_runtime
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient


def build_default_runtime(
    run_control: RunControlStore | None = None,
) -> ResearchGraphRuntime:
    """建立不依赖外部服务的默认 runtime。"""

    control = run_control or InMemoryRunControlStore()
    return create_research_runtime(
        MockLLMClient(),
        MockSearchClient(),
        run_control=control,
    )


def get_runtime(request: Request) -> ResearchGraphRuntime:
    """从应用状态获取 runtime。"""

    return request.app.state.research_runtime


def get_run_control(request: Request) -> RunControlStore | None:
    """从应用状态获取运行控制存储。"""

    return request.app.state.run_control
