"""FastAPI 应用入口。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.run_control import InMemoryRunControlStore, RunControlStore
from app.graph.runtime import ResearchGraphRuntime
from app.persistence.repository import ResearchRepository

from .dependencies import build_configured_runtime
from .research import router as research_router
from .schemas import HealthResponse


def _check_database_schema(engine: Engine) -> None:
    """在 API 启动时验证连接和当前 Repository 所需的表结构。"""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        inspector = inspect(connection)
        required_columns = {
            "research_runs": {"session_id", "status", "error", "state_data"},
            "research_events": {"session_id", "sequence", "event_type", "data"},
        }
        missing = []
        for table, expected_columns in required_columns.items():
            if not inspector.has_table(table):
                missing.append(f"{table} 表不存在")
                continue
            actual_columns = {column["name"] for column in inspector.get_columns(table)}
            absent_columns = expected_columns - actual_columns
            if absent_columns:
                missing.append(f"{table} 缺少字段 {', '.join(sorted(absent_columns))}")
        if missing:
            details = "；".join(missing)
            raise RuntimeError(
                f"PostgreSQL 数据库结构未升级到当前版本：{details}。"
                "请先运行 `python -m alembic -c alembic.ini upgrade head`。"
            )


def create_app(
    runtime: ResearchGraphRuntime | None = None,
    *,
    run_control: RunControlStore | None = None,
    repository: ResearchRepository | None = None,
    checkpointer=None,
) -> FastAPI:
    """创建 API 应用；配置 ``DATABASE_URL`` 后自动接入 PostgreSQL Repository。"""

    control = run_control or getattr(runtime, "run_control", None) or InMemoryRunControlStore()
    injected_repository = repository or getattr(runtime, "repository", None)
    runtime_was_injected = runtime is not None
    repository_was_injected = injected_repository is not None
    effective_runtime = runtime or build_configured_runtime(
        control, injected_repository, checkpointer
    )
    effective_repository = injected_repository or getattr(effective_runtime, "repository", None)
    database_engine = getattr(effective_repository, "engine", None)
    owns_database_engine = (
        not runtime_was_injected
        and not repository_was_injected
        and bool(getattr(effective_repository, "owns_engine", False))
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            if database_engine is not None:
                _check_database_schema(database_engine)
            yield
        finally:
            if owns_database_engine and effective_repository is not None:
                effective_repository.close()

    app = FastAPI(title="Information DeepResearch API", version="2", lifespan=lifespan)
    app.state.run_control = control
    app.state.repository = effective_repository
    app.state.research_runtime = effective_runtime
    app.state.database_engine = database_engine
    app.include_router(research_router)

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        if database_engine is None:
            database_status = "not_configured" if effective_repository is None else "configured"
            return HealthResponse(status="ok", database=database_status)
        try:
            with database_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return HealthResponse(status="degraded", database="unavailable")
        return HealthResponse(status="ok", database="connected")

    return app


app = create_app()

__all__ = ["app", "create_app"]
