"""加载项目根目录的本地环境文件。"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


def load_project_env() -> Path | None:
    """加载项目根目录的 ``.env``；已有系统环境变量优先。"""

    if not ENV_FILE.is_file():
        return None
    load_dotenv(dotenv_path=ENV_FILE, override=False)
    return ENV_FILE


__all__ = ["ENV_FILE", "PROJECT_ROOT", "load_project_env"]
