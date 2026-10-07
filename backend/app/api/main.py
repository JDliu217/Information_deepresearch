"""FastAPI 应用入口。"""

from __future__ import annotations

from fastapi import FastAPI

from app.core.run_control import InMemoryRunControlStore, RunControlStore
from app.graph.runtime import ResearchGraphRuntime

from .dependencies import build_default_runtime
from .schemas import HealthResponse


def create_app(
    runtime: ResearchGraphRuntime | None = None,
    *,
    run_control: RunControlStore | None = None,
) -> FastAPI:
    """创建 API 应用；参数注入让测试和部署不依赖全局单例。"""

    control = run_control or InMemoryRunControlStore()
    app = FastAPI(title="Information DeepResearch API", version="2")
    app.state.run_control = control
    app.state.research_runtime = runtime or build_default_runtime(control)

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return app


app = create_app()

__all__ = ["app", "create_app"]
