"""从研究证据中生成结构化数据、知识图谱和 ECharts 配置。"""

from __future__ import annotations

import uuid
from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Chart, DataPoint
from app.domain.state import ResearchState

from .base import BaseAgent


class DataAnalystAgent(BaseAgent):
    """按参考 DataAnalyst 的三阶段顺序分析研究事实。"""

    name = "data_analyst"

    DATA_EXTRACTION_PROMPT = """你是专业的数据分析师，擅长从文本中提取结构化数据。

## 研究主题
{query}

## 搜索结果
{search_results}

## 任务
从以上搜索结果中提取所有可量化的数据点，包括：
1. 与研究主题有关的数量、金额、年龄、时长、日期或年代等明确数值
2. 来源中明确报告的比率、变化幅度、排名或分类占比（仅当主题涉及这些信息时）
3. 同一指标在不同时间或类别下的可比较数据
4. 与研究问题直接相关、且原始材料明确给出的其他数值

## 输出要求
请输出JSON格式：
```json
{{
    "data_points": [
        {{
            "id": "dp_001",
            "name": "材料中指标的名称",
            "value": 0,
            "unit": "材料中的单位",
            "year": null,
            "source": "材料中的来源名称",
            "category": "与主题相符的类别",
            "confidence": 0.0
        }}
    ],
    "time_series": [
        {{
            "id": "ts_001",
            "metric": "材料中的指标名称",
            "unit": "材料中的单位",
            "data": [
                {{"year": 0, "value": 0}}
            ],
            "source": "材料中的来源名称"
        }}
    ],
    "distributions": [
        {{
            "id": "dist_001",
            "name": "材料中明确报告的分类指标",
            "year": null,
            "data": [
                {{"category": "材料中的类别", "value": 0, "unit": "材料中的单位"}}
            ],
            "source": "材料中的来源名称"
        }}
    ],
    "insights": ["仅根据输入材料归纳出的洞察"]
}}
```

注意：
- 只提取有明确来源的数据
- JSON 示例中的 0、占位名称和空值只用于说明字段，不是研究事实；不能复制为输出数据
- confidence表示数据可信度(0-1)
- 如果没有找到相关数据，返回空数组"""

    KNOWLEDGE_GRAPH_PROMPT = """你是知识图谱专家，擅长从文本中提取实体和关系。

## 研究主题
{query}

## 文本内容
{content}

## 任务
从以上文本中提取实体和关系，构建知识图谱。

## 实体类型定义
- core: 研究主题中的核心实体或概念
- person: 人物
- organization: 组织或机构
- place: 地点
- event: 事件
- work: 作品
- technology: 技术
- policy: 政策
- product: 产品
- 也可根据材料使用其他准确的实体类型；不要为了匹配固定类型而误分类

## 输出要求
请输出JSON格式：
```json
{{
    "nodes": [
        {{"id": "node_1", "name": "材料中的实体名称", "type": "实体类型", "importance": 8}},
        {{"id": "node_2", "name": "与主题相关的另一实体", "type": "实体类型", "importance": 6}}
    ],
    "edges": [
        {{"source": "node_1", "target": "node_2", "relation": "材料明确说明的关系"}}
    ]
}}
```

注意：
- importance范围1-10，表示节点重要性
- 核心概念(core)的importance最高
- 提取5-15个最重要的实体
- 关系要简洁，2-4个字"""

    CHART_GENERATION_PROMPT = """你是数据可视化专家，擅长生成ECharts图表配置。

## 研究主题
{query}

## 可用数据
{data}

## 任务
根据数据生成合适的ECharts图表配置，选择最能展示数据特点的图表类型。

## 图表类型选择规则
- 时间序列数据 → line (折线图)
- 分类比较数据 → bar (柱状图)
- 占比分布数据 → pie (饼图)
- 进度/百分比 → horizontal_bar (横向进度条)
- 多维对比 → radar (雷达图)

## 设计要求
1. 配色使用简约专业色系：
   - 主色：#1677ff (蓝)
   - 辅助色：#52c41a (绿), #722ed1 (紫), #fa8c16 (橙), #eb2f96 (粉)
2. 标题简洁明了
3. 不要过多装饰，保持简约

## 输出要求
请输出JSON格式：
```json
{{
    "charts": [
        {{
            "id": "chart_001",
            "title": "根据输入数据确定的图表标题",
            "subtitle": "指标名称和时间或分类范围",
            "type": "line",
            "echarts_option": {{
                "grid": {{"left": "3%", "right": "4%", "bottom": "3%", "containLabel": true}},
                "xAxis": {{
                    "type": "category",
                    "data": ["输入数据中的类别或时间"],
                    "axisLine": {{"lineStyle": {{"color": "#e8e8e8"}}}},
                    "axisLabel": {{"color": "#666"}}
                }},
                "yAxis": {{
                    "type": "value",
                    "axisLine": {{"show": false}},
                    "splitLine": {{"lineStyle": {{"color": "#f0f0f0"}}}}
                }},
                "series": [{{
                    "type": "line",
                    "data": [0],
                    "smooth": true,
                    "symbol": "circle",
                    "symbolSize": 8,
                    "itemStyle": {{"color": "#1677ff"}},
                    "lineStyle": {{"width": 3}},
                    "areaStyle": {{"color": {{"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1, "colorStops": [{{"offset": 0, "color": "rgba(22,119,255,0.2)"}}, {{"offset": 1, "color": "rgba(22,119,255,0)"}}]}}}}
                }}]
            }}
        }},
        {{
            "id": "chart_002",
            "title": "根据输入数据确定的分类对比",
            "subtitle": "输入数据中的分类范围和指标",
            "type": "horizontal_bar",
            "echarts_option": {{
                "grid": {{"left": "25%", "right": "15%", "top": "5%", "bottom": "5%"}},
                "xAxis": {{"type": "value", "show": false, "max": 100}},
                "yAxis": {{
                    "type": "category",
                    "data": ["输入数据中的类别"],
                    "axisLine": {{"show": false}},
                    "axisTick": {{"show": false}},
                    "axisLabel": {{"color": "#333", "fontSize": 13}}
                }},
                "series": [{{
                    "type": "bar",
                    "data": [{{"value": 0}}],
                    "barWidth": 12,
                    "label": {{
                        "show": true,
                        "position": "right",
                        "formatter": "{{c}}%",
                        "color": "#666"
                    }},
                    "backgroundStyle": {{"color": "#f5f5f5"}},
                    "showBackground": true
                }}]
            }}
        }}
    ]
}}
```

注意：图表字段中的名称和数值只展示结构。输出时只能填入上方可用数据中的类别和数值；不得复制占位文本或自行补造数值。没有可比较的数据时返回空 charts 列表。"""

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
        extracted_data = await self._extract_data(state)
        knowledge_graph = await self._build_knowledge_graph(state)
        charts = await self._generate_charts(state, extracted_data)

        # DeepScout's active DataAnalyst stage replaces the graph built during
        # source analysis with its graph from the first 15 facts.
        state.knowledge_graph = knowledge_graph
        state.charts.extend(charts)
        state.phase = "analyzing"
        return state

    async def _extract_data(self, state: ResearchState) -> dict[str, Any]:
        """Extract structured data from the first 20 facts, as in V2 DataAnalyst."""

        search_results = [
            f"- {fact.get('content', '')} (来源: {fact.get('source_name', '未知')})"
            for fact in state.facts[:20]
        ]
        if not search_results:
            return {
                "data_points": [],
                "time_series": [],
                "distributions": [],
                "insights": [],
            }

        search_results_text = "\n".join(search_results)
        payload = {
            "mode": "data_extraction",
            "query": state.query,
            "search_results": search_results_text,
        }
        result = await self._complete_json(
            payload,
            system_prompt="你是专业的数据分析师，擅长从文本中提取结构化数据。请输出JSON格式。",
            user_prompt=self.DATA_EXTRACTION_PROMPT.format(
                query=state.query,
                search_results=search_results_text,
            ),
            temperature=0.2,
            max_tokens=16000,
        )
        extracted_data = self._validate_data_extraction(result)

        # Map reference dictionaries into the current domain DataPoint model.
        # The reference appends both data points and insights on each pass.
        self._append_structured_data_points(
            state.data_points,
            extracted_data["data_points"],
        )
        state.insights.extend(extracted_data["insights"])
        return extracted_data

    async def _build_knowledge_graph(
        self,
        state: ResearchState,
    ) -> dict[str, Any]:
        """Build a graph from the first 15 fact bodies, as in V2 DataAnalyst."""

        content_parts = [
            str(fact.get("content", ""))
            for fact in state.facts[:15]
        ]
        if not content_parts:
            return {"nodes": [], "edges": []}

        content = "\n".join(content_parts)
        payload = {
            "mode": "knowledge_graph",
            "query": state.query,
            "content": content,
        }
        result = await self._complete_json(
            payload,
            system_prompt="你是知识图谱专家，擅长从文本中提取实体和关系。请输出JSON格式。",
            user_prompt=self.KNOWLEDGE_GRAPH_PROMPT.format(
                query=state.query,
                content=content,
            ),
            temperature=0.2,
            max_tokens=16000,
        )
        return self._validate_knowledge_graph(result)

    async def _generate_charts(
        self,
        state: ResearchState,
        extracted_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate charts only when extracted data can support a chart."""

        chart_data = {
            "data_points": extracted_data.get("data_points", []),
            "time_series": extracted_data.get("time_series", []),
            "distributions": extracted_data.get("distributions", []),
            "existing_data_points": state.data_points[:10],
        }
        total_data = sum(
            len(chart_data[field])
            for field in ("data_points", "time_series", "distributions")
        )
        if total_data == 0:
            return []

        payload = {
            "mode": "chart_generation",
            "query": state.query,
            "data": chart_data,
        }
        result = await self._complete_json(
            payload,
            system_prompt="你是数据可视化专家，擅长生成ECharts图表配置。请输出JSON格式。",
            user_prompt=self.CHART_GENERATION_PROMPT.format(
                query=state.query,
                data=str(chart_data),
            ),
            temperature=0.3,
            max_tokens=16000,
        )
        _, charts = self._validate_result(result)
        return charts

    @staticmethod
    def _format_search_results(facts: list[dict[str, Any]]) -> str:
        return "\n".join(
            f"- {fact.get('content', '')} (来源: {fact.get('source_name') or fact.get('source_title', '未知')})"
            for fact in facts
        )

    @staticmethod
    def _validate_data_extraction(value: Any) -> dict[str, Any]:
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
        }

    @staticmethod
    def _append_structured_data_points(
        target: list[dict[str, Any]],
        values: list[dict[str, Any]],
    ) -> None:
        for item in values:
            name = str(item.get("name", "")).strip()
            if not name or item.get("value") is None:
                continue
            try:
                confidence = float(item.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError) as exc:
                raise ValueError("DataAnalyst 数据点 confidence 无效") from exc
            if not 0 <= confidence <= 1:
                raise ValueError("DataAnalyst 数据点 confidence 必须在 0 到 1 之间")
            year = item.get("year")
            year_label = ""
            if year is not None:
                if isinstance(year, bool):
                    year_label = str(year)
                    year = None
                elif isinstance(year, int):
                    pass
                elif isinstance(year, float) and year.is_integer():
                    year = int(year)
                else:
                    raw_year = str(year).strip()
                    try:
                        year = int(raw_year)
                    except (TypeError, ValueError):
                        # The reference agent accepts descriptive periods such
                        # as "2016-2023".  DataPoint.year models a single year,
                        # so retain the original label separately instead of
                        # rejecting the complete analysis result.
                        year_label = raw_year
                        year = None
            normalized = DataPoint(
                id=str(item.get("id", "")).strip() or f"dp_{uuid.uuid4().hex[:8]}",
                name=name,
                value=item["value"],
                unit=str(item.get("unit", "")).strip(),
                year=year,
                source=str(item.get("source", "")).strip(),
                confidence=confidence,
            ).to_dict()
            if year_label:
                normalized["year_label"] = year_label
            # Keep reference fields such as category and any future metadata
            # that the current DataPoint schema does not model yet.
            target.append({**item, **normalized})

    @staticmethod
    def _validate_knowledge_graph(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("DataAnalyst 知识图谱结果必须是对象")
        nodes = value.get("nodes", []) or []
        edges = value.get("edges", []) or []
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("DataAnalyst 知识图谱 nodes 和 edges 必须是列表")

        normalized_nodes = []
        for index, node in enumerate(nodes, start=1):
            if not isinstance(node, dict):
                raise ValueError("DataAnalyst 知识图谱节点必须是对象")
            try:
                importance = float(node.get("importance", 5))
            except (TypeError, ValueError) as exc:
                raise ValueError("DataAnalyst 知识图谱节点 importance 无效") from exc
            normalized_nodes.append({**node, "size": 20 + importance * 3})

        if not all(isinstance(edge, dict) for edge in edges):
            raise ValueError("DataAnalyst 知识图谱边必须是对象")
        return {"nodes": normalized_nodes, "edges": edges}

    @classmethod
    def _validate_result(
        cls,
        value: Any,
    ) -> tuple[list[str], list[dict[str, Any]]]:
        if not isinstance(value, dict):
            raise ValueError("DataAnalyst 返回结果必须是对象")

        raw_insights = value.get("insights", []) or []
        if not isinstance(raw_insights, list) or not all(
            isinstance(insight, str) and insight.strip() for insight in raw_insights
        ):
            raise ValueError("DataAnalyst 的 insights 必须是非空字符串列表")
        raw_charts = value.get("charts", []) or []
        if not isinstance(raw_charts, list):
            raise ValueError("DataAnalyst 的 charts 必须是列表")

        charts: list[dict[str, Any]] = []
        chart_ids: set[str] = set()
        for index, item in enumerate(raw_charts, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"DataAnalyst 的第 {index} 个图表不是对象")
            chart_id = str(item.get("id", "")).strip() or f"chart_{uuid.uuid4().hex[:8]}"
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
                raise ValueError(f"DataAnalyst 的第 {index} 个图表 echarts_option 必须是对象")
            series = echarts_option.get("series")
            if not isinstance(series, list) or not series:
                raise ValueError(
                    f"DataAnalyst 的第 {index} 个图表 echarts_option.series 必须是非空列表"
                )
            if not all(isinstance(series_item, dict) for series_item in series):
                raise ValueError(f"DataAnalyst 的第 {index} 个图表 series 元素必须是对象")
            data = item.get("data") or {}
            if not isinstance(data, dict):
                raise ValueError(f"DataAnalyst 的第 {index} 个图表 data 必须是对象")
            if item.get("subtitle"):
                data = {**data, "subtitle": str(item["subtitle"])}

            charts.append(
                Chart(
                    id=chart_id,
                    title=title,
                    chart_type=chart_type,
                    data=data,
                    echarts_option=echarts_option,
                    code=str(item.get("code", "")).strip(),
                    image_path=item.get("image_path"),
                    image_base64=item.get("image_base64"),
                    section_id=(str(item["section_id"]).strip() if item.get("section_id") else None),
                ).to_dict()
            )

        return [item.strip() for item in raw_insights], charts
