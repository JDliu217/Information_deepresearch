"""DeepResearch V2 使用的基础领域对象。

这些对象先只描述数据形状，不负责调用 LLM、搜索服务或数据库。
把数据形状单独放在这里，可以让后续 Agent 共享同一套结构。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


SectionType = Literal["qualitative", "quantitative", "mixed"]
SectionStatus = Literal["pending", "researching", "drafted", "reviewed", "final"]
HypothesisStatus = Literal[
    "unverified",
    "supported",
    "refuted",
    "partially_supported",
]
ChartType = Literal[
    "line",
    "bar",
    "pie",
    "scatter",
    "table",
    "heatmap",
    "horizontal_bar",
    "radar",
]
IssueType = Literal[
    "missing_source",
    "logic_error",
    "bias",
    "hallucination",
    "outdated",
    "incomplete",
]
IssueSeverity = Literal["critical", "major", "minor"]


@dataclass
class Section:
    """研究报告中的一个章节。"""

    id: str
    title: str
    description: str = ""
    section_type: SectionType = "mixed"
    status: SectionStatus = "pending"
    content: str = ""
    sources: list[str] = field(default_factory=list)
    subsections: list[Section] = field(default_factory=list)
    requires_data: bool = False
    requires_chart: bool = False
    priority: int = 0
    search_queries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换成可以放入 ResearchState 的普通字典。"""
        return asdict(self)


@dataclass
class Hypothesis:
    """研究开始时提出、再由证据验证的假设。"""

    id: str
    content: str
    status: HypothesisStatus = "unverified"
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataPoint:
    """可以被分析或绘图使用的结构化数据点。"""

    id: str
    name: str
    value: Any
    unit: str = ""
    year: int | None = None
    source: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Chart:
    """DataAnalyst 或 CodeWizard 生成的图表结果。"""

    id: str
    title: str
    chart_type: ChartType
    data: dict[str, Any] = field(default_factory=dict)
    echarts_option: dict[str, Any] = field(default_factory=dict)
    code: str = ""
    image_path: str | None = None
    image_base64: str | None = None
    section_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CriticFeedback:
    """审核 Agent 针对报告或章节提出的一条问题。"""

    id: str
    target_section: str
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    suggestion: str
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

