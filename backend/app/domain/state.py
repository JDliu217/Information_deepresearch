"""DeepResearch V2 的共享工作状态。

所有研究 Agent 读取和更新同一个任务状态。状态只保存数据，流程逻辑
由 workflow 编排，领域对象由 domain.models 定义。
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
    max_iterations: int = 3

    # 规划结果
    # V2 章节大纲。后续 Planner 会逐步使用 domain.models.Section。
    outline: list[dict[str, Any]] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    mind_map: dict[str, Any] = field(default_factory=dict)
    knowledge_graph: dict[str, Any] = field(
        default_factory=lambda: {"nodes": [], "edges": []}
    )
    pending_search_queries: list[str] = field(default_factory=list)
    pending_search_contexts: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    # Planner 的结构化响应、逐次校验结论和耗时，用于复盘规划失败。
    # 仅存储有大小限制且已脱敏的 LLM 响应文本，不包含请求凭证。
    planner_diagnostics: list[dict[str, Any]] = field(default_factory=list)

    # 研究证据
    # 原始搜索结果；事实提取和后续分析都从这里读取。
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
    review_result: dict[str, Any] = field(default_factory=dict)
    critic_feedback: list[dict[str, Any]] = field(default_factory=list)
    # 每轮保留 Critic 的原始评分和问题变化，用于判断修订是否真的改善报告。
    review_history: list[dict[str, Any]] = field(default_factory=list)
    unresolved_issues: int = 0
    quality_score: float = 0.0

    # 运行记录
    logs: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
