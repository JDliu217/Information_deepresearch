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

    # 当前阶段：init / planning / researching / analyzing / writing /
    # reviewing / re_researching / revising / completed
    phase: str = "init"

    # 审核循环次数
    iteration: int = 0
    max_iterations: int = 1

    # 规划结果
    plan: list[dict[str, Any]] = field(default_factory=list)
    # V2 章节大纲。当前仍用字典保存，后续 Planner 会逐步使用 Section。
    outline: list[dict[str, Any]] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    mind_map: dict[str, Any] = field(default_factory=dict)
    knowledge_graph: dict[str, Any] = field(
        default_factory=lambda: {"nodes": [], "edges": []}
    )
    pending_search_queries: list[str] = field(default_factory=list)

    # 研究证据
    sources: list[dict[str, Any]] = field(default_factory=list)
    # raw_sources 保留原始搜索结果，sources 继续兼容 iteration-01 Agent。
    raw_sources: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    data_points: list[dict[str, Any]] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)

    # 写作和审核结果
    draft_sections: dict[str, str] = field(default_factory=dict)
    final_report: str = ""
    charts: list[dict[str, Any]] = field(default_factory=list)
    code_executions: list[dict[str, Any]] = field(default_factory=list)
    review: dict[str, Any] = field(default_factory=dict)
    critic_feedback: list[dict[str, Any]] = field(default_factory=list)
    unresolved_issues: int = 0
    quality_score: float = 0.0

    # 运行记录
    logs: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
