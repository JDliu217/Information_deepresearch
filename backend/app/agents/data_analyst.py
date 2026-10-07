"""从研究证据中生成结构化洞察和 ECharts 配置。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Chart
from app.domain.state import ResearchState

from .base import BaseAgent


class DataAnalystAgent(BaseAgent):
    """把事实和数据点转换成报告可以使用的分析结果。"""

    name = "data_analyst"
    DATA_EXTRACTION_SYSTEM = """你是 DeepResearch 的数据分析 Agent。只使用输入中的事实和数据点，
不创造数字或来源。区分描述性统计、相关性、因果关系和预测；任何洞察必须可追溯。"""
    DATA_EXTRACTION_PROMPT = """请从已验证事实中提取结构化数据、时间序列、分布和有证据边界的洞察。
如果数据不足，返回空数据或明确说明缺口。"""
    KNOWLEDGE_GRAPH_PROMPT = """请根据事实内容生成知识图谱节点和关系。节点名称要稳定，关系必须能由
事实直接支持；合并已有图谱时不要重复节点和边。"""
    CHART_GENERATION_PROMPT = """请根据结构化数据生成必要的 ECharts 配置。时间序列用 line，分类比较
用 bar，占比用 pie；数据不足时返回空 charts。series 必须非空，data_point_ids 必须引用已有数据点。"""
    allowed_chart_types = {
        "line",
        "bar",
        "pie",
        "scatter",
        "table",
        "heatmap",
        "horizontal_bar",
        "radar",
    }

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.facts:
            raise ValueError("没有可供数据分析的事实")

        payload = {
            "query": state.query,
            "facts": state.facts,
            "data_points": state.data_points,
            "knowledge_graph": state.knowledge_graph,
            "instruction": (
                "根据已有事实和数据点提炼可验证的洞察；如果有足够数据，"
                "生成一个或多个可直接交给 ECharts 的配置。不要编造来源中不存在的数据。"
            ),
        }
        result = await self._complete_json(
            payload,
            system_prompt=self.DATA_EXTRACTION_SYSTEM,
            user_prompt=self._render_prompt(self.DATA_EXTRACTION_PROMPT, payload),
        )
        insights, charts = self._validate_result(result)
        state.insights = self._merge_insights(state.insights, insights)
        self._upsert_charts(state.charts, charts)
        state.phase = "analyzing"
        return state

    @classmethod
    def _validate_result(
        cls,
        value: Any,
    ) -> tuple[list[str], list[dict[str, Any]]]:
        if not isinstance(value, dict):
            raise ValueError("DataAnalyst 返回结果必须是对象")

        raw_insights = value.get("insights", [])
        if raw_insights is None:
            raw_insights = []
        if not isinstance(raw_insights, list) or not all(
            isinstance(insight, str) and insight.strip() for insight in raw_insights
        ):
            raise ValueError("DataAnalyst 的 insights 必须是非空字符串列表")
        insights = [insight.strip() for insight in raw_insights]

        raw_charts = value.get("charts", [])
        if raw_charts is None:
            raw_charts = []
        if not isinstance(raw_charts, list):
            raise ValueError("DataAnalyst 的 charts 必须是列表")

        charts: list[dict[str, Any]] = []
        chart_ids: set[str] = set()
        for index, item in enumerate(raw_charts, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"DataAnalyst 的第 {index} 个图表不是对象")

            chart_id = str(item.get("id", f"chart_{index}")).strip() or f"chart_{index}"
            if chart_id in chart_ids:
                raise ValueError(f"DataAnalyst 的图表 id 重复: {chart_id}")
            chart_ids.add(chart_id)

            title = str(item.get("title", "")).strip()
            if not title:
                raise ValueError(f"DataAnalyst 的第 {index} 个图表缺少 title")

            chart_type = str(item.get("type", item.get("chart_type", ""))).strip()
            if chart_type not in cls.allowed_chart_types:
                raise ValueError(f"DataAnalyst 的第 {index} 个图表 type 无效")

            echarts_option = item.get("echarts_option")
            if not isinstance(echarts_option, dict):
                raise ValueError(
                    f"DataAnalyst 的第 {index} 个图表 echarts_option 必须是对象"
                )
            series = echarts_option.get("series")
            if not isinstance(series, list) or not series:
                raise ValueError(
                    f"DataAnalyst 的第 {index} 个图表 echarts_option.series 必须是非空列表"
                )
            if not all(isinstance(series_item, dict) for series_item in series):
                raise ValueError(
                    f"DataAnalyst 的第 {index} 个图表 series 元素必须是对象"
                )

            data = item.get("data", {})
            if data is None:
                data = {}
            if not isinstance(data, dict):
                raise ValueError(f"DataAnalyst 的第 {index} 个图表 data 必须是对象")

            chart = Chart(
                id=chart_id,
                title=title,
                chart_type=chart_type,
                data=data,
                echarts_option=echarts_option,
                code=str(item.get("code", "")).strip(),
                image_path=item.get("image_path"),
                image_base64=item.get("image_base64"),
                section_id=(str(item["section_id"]).strip() if item.get("section_id") else None),
            )
            charts.append(chart.to_dict())

        return insights, charts

    @staticmethod
    def _merge_insights(existing: list[str], new_insights: list[str]) -> list[str]:
        """按文本去重，保留洞察首次出现的顺序。"""
        merged: list[str] = []
        seen: set[str] = set()
        for insight in [*existing, *new_insights]:
            insight = str(insight).strip()
            if insight and insight not in seen:
                merged.append(insight)
                seen.add(insight)
        return merged

    @staticmethod
    def _upsert_charts(
        target: list[dict[str, Any]],
        charts: list[dict[str, Any]],
    ) -> None:
        """按图表 id 更新结果，避免补充研究重复添加相同图表。"""
        positions = {
            str(chart.get("id", "")).strip(): index
            for index, chart in enumerate(target)
            if chart.get("id")
        }
        for chart in charts:
            chart_id = chart["id"]
            if chart_id in positions:
                target[positions[chart_id]] = chart
            else:
                positions[chart_id] = len(target)
                target.append(chart)
