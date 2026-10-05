"""DeepResearch 的共享工作状态。

第一轮先用一个普通 dataclass 表达状态。
后面的 Planner、Researcher、Writer 和 Critic 都读写同一个对象，
这样可以清楚看到信息如何在研究流程中流动。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class ResearchState:
    """一次研究任务从开始到结束所需要的全部核心数据。"""

    # 用户输入和任务身份
    query: str
    session_id: str = field(default_factory=lambda: str(uuid4()))

    # 当前阶段：init / planning / researching / writing / reviewing / completed
    phase: str = "init"

    # 审核循环次数
    iteration: int = 0
    max_iterations: int = 1

    # 规划结果
    plan: list[dict[str, Any]] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)

    # 研究证据
    sources: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)

    # 写作和审核结果
    final_report: str = ""
    review: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0

    # 错误记录
    errors: list[str] = field(default_factory=list)
