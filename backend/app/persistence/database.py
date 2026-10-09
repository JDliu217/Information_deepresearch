"""SQLAlchemy Engine 和 Session 工厂。"""

from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.env import load_project_env


@dataclass(frozen=True)
class DatabaseSettings:
    """数据库连接配置；密码只从环境变量读取。"""

    url: str | None = None
    echo: bool = False

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        load_project_env()
        return cls(
            url=os.getenv("DATABASE_URL") or None,
            echo=os.getenv("DATABASE_ECHO", "0").lower() in {"1", "true", "yes"},
        )


def create_database_engine(settings: DatabaseSettings | None = None) -> Engine:
    """按配置创建 Engine；真正连接数据库发生在首次执行 SQL 时。"""

    settings = settings or DatabaseSettings.from_env()
    if not settings.url:
        raise ValueError("DATABASE_URL 未配置，无法创建 PostgreSQL Engine")
    return create_engine(settings.url, echo=settings.echo, pool_pre_ping=True)


def create_session_factory(
    engine: Engine,
) -> sessionmaker[Session]:
    """创建显式 Session 工厂，不在 Agent 中隐藏数据库连接。"""

    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
