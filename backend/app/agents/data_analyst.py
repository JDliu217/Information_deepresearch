"""从研究证据中生成结构化洞察和 ECharts 配置。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Chart, DataPoint
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

        extraction_payload = {
            "mode": "data_extraction",
            "query": state.query,
            "facts": self._fact_summaries(state.facts[:20]),
            "data_points": state.data_points[:20],
            "instruction": "从前 20 条事实摘要提取结构化数据、时间序列、分布和有证据边界的洞察。",
        }
        extracted = await self._complete_json(
            extraction_payload,
            system_prompt=self.DATA_EXTRACTION_SYSTEM,
            user_prompt=self._render_prompt(self.DATA_EXTRACTION_PROMPT, extraction_payload),
        )

        extracted_data = self._validate_data_extraction(extracted)
        self._append_structured_data_points(state.data_points, extracted_data["data_points"])
        state.insights = self._merge_insights(
            state.insights,
            [*extracted_data["insights"], *extracted_data["time_series_insights"]],
        )

        graph_payload = {
            "mode": "knowledge_graph",
            "query": state.query,
            "facts": self._fact_summaries(state.facts[:15]),
            "knowledge_graph": state.knowledge_graph,
        }
        graph_result = await self._complete_json(
            graph_payload,
            system_prompt=self.DATA_EXTRACTION_SYSTEM,
            user_prompt=self._render_prompt(self.KNOWLEDGE_GRAPH_PROMPT, graph_payload),
        )
        self._merge_knowledge_graph(state.knowledge_graph, graph_result)

        chart_candidates = (
            extracted_data["data_points"]
            or extracted_data["time_series"]
            or extracted_data["distributions"]
            or state.data_points[:10]
        )
        if chart_candidates:
            chart_payload = {
                "mode": "chart_generation",
                "query": state.query,
                "data": {
                    "data_points": extracted_data["data_points"],
                    "time_series": extracted_data["time_series"],
                    "distributions": extracted_data["distributions"],
                    "existing_data_points": state.data_points[:10],
                },
            }
            chart_result = await self._complete_json(
                chart_payload,
                system_prompt=self.DATA_EXTRACTION_SYSTEM,
                user_prompt=self._render_prompt(self.CHART_GENERATION_PROMPT, chart_payload),
            )
            _, charts = self._validate_result(chart_result)
            self._upsert_charts(state.charts, charts)
        state.phase = "analyzing"
        return state

    @staticmethod
    def _fact_summaries(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "id": fact.get("id", ""),
                "content": str(fact.get("content", "")).strip()[:500],
                "source_title": fact.get("source_title", ""),
                "source_url": fact.get("source_url", ""),
                "data_points": fact.get("data_points", []),
            }
            for fact in facts
        ]

    @classmethod
    def _validate_data_extraction(cls, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("DataAnalyst 数据提取结果必须是对象")

        def list_of_dicts(field: str) -> list[dict[str, Any]]:
            raw = value.get(field, []) or []
            if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
                raise ValueError(f"DataAnalyst 的 {field} 必须是对象列表")
            return raw

        raw_insights = value.get("insights", []) or []
        if not isinstance(raw_insights, list) or not all(
            isinstance(item, str) and item.strip() for item in raw_insights
        ):
            raise ValueError("DataAnalyst 数据提取的 insights 必须是字符串列表")
        return {
            "data_points": list_of_dicts("data_points"),
            "time_series": list_of_dicts("time_series"),
            "distributions": list_of_dicts("distributions"),
            "insights": [item.strip() for item in raw_insights],
            "time_series_insights": [],
        }

    @staticmethod
    def _append_structured_data_points(
        target: list[dict[str, Any]],
        values: list[dict[str, Any]],
    ) -> None:
        seen = {
            (
                str(item.get("name", "")).strip(),
                str(item.get("value", "")).strip(),
                str(item.get("unit", "")).strip(),
                str(item.get("year", "")).strip(),
                str(item.get("source", "")).strip(),
            )
            for item in target
        }
        for index, item in enumerate(values, start=1):
            name = str(item.get("name", "")).strip()
            if not name or item.get("value") is None:
                continue
            normalized = {
                "id": str(item.get("id", "")).strip() or f"dp_{len(target) + 1}",
                "name": name,
                "value": item.get("value"),
                "unit": str(item.get("unit", "")).strip(),
                "year": item.get("year"),
                "source": str(item.get("source", "")).strip(),
                "confidence": float(item.get("confidence", 0.0) or 0.0),
            }
            key = (
                normalized["name"],
                str(normalized["value"]).strip(),
                normalized["unit"],
                str(normalized["year"] or "").strip(),
                normalized["source"],
            )
            if key not in seen:
                target.append(DataPoint(**normalized).to_dict())
                seen.add(key)

    @staticmethod
    def _merge_knowledge_graph(target: dict[str, Any], value: Any) -> None:
        if not isinstance(value, dict):
            raise ValueError("DataAnalyst 知识图谱结果必须是对象")
        nodes = value.get("nodes", []) or []
        edges = value.get("edges", []) or []
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("DataAnalyst 知识图谱 nodes 和 edges 必须是列表")
        target_nodes = target.setdefault("nodes", [])
        target_edges = target.setdefault("edges", [])
        node_keys = {
            str(node.get("name", node.get("id", ""))).strip()
            for node in target_nodes
            if isinstance(node, dict)
        }
        for node in nodes:
            if not isinstance(node, dict):
                raise ValueError("DataAnalyst 知识图谱节点必须是对象")
            name = str(node.get("name", node.get("id", ""))).strip()
            if not name or name in node_keys:
                continue
            target_nodes.append(node)
            node_keys.add(name)
        edge_keys = {
            (
                str(edge.get("source", "")).strip(),
                str(edge.get("target", "")).strip(),
                str(edge.get("relation", "")).strip(),
            )
            for edge in target_edges
            if isinstance(edge, dict)
        }
        for edge in edges:
            if not isinstance(edge, dict):
                raise ValueError("DataAnalyst 知识图谱边必须是对象")
            key = (
                str(edge.get("source", "")).strip(),
                str(edge.get("target", "")).strip(),
                str(edge.get("relation", "")).strip(),
            )
            if key not in edge_keys:
                target_edges.append(edge)
                edge_keys.add(key)

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
