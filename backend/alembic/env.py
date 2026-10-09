"""Alembic 迁移环境。"""

from __future__ import annotations

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.persistence.base import Base
from app.persistence import models  # noqa: F401 - 注册模型元数据
from app.core.env import load_project_env


config = context.config
database_url = config.get_main_option("sqlalchemy.url")
if not database_url:
    load_project_env()
    database_url = os.getenv("DATABASE_URL")
if database_url:
    # Alembic ConfigParser treats percent signs as interpolation markers.
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
elif not config.get_main_option("sqlalchemy.url"):
    raise RuntimeError(
        "DATABASE_URL 未配置。请在项目根目录 .env 中填写 PostgreSQL 连接地址后再运行迁移。"
    )
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
