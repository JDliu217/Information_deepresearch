import asyncio
import unittest

from app.agents.data_analyst import DataAnalystAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class InvalidAnalysisClient(LLMClient):
    async def complete_json(self, role, payload):
        if payload["mode"] == "data_extraction":
            return {"data_points": [{"name": "指标", "value": 1}], "insights": []}
        if payload["mode"] == "knowledge_graph":
            return {"nodes": [], "edges": []}
        return {
            "insights": ["有效洞察"],
            "charts": [
                {
                    "id": "chart-1",
                    "title": "无效图表",
                    "type": "bar",
                    "echarts_option": {"xAxis": {}, "series": "不是列表"},
                }
            ],
        }

    async def complete_text(self, role, payload):
        return ""


class CapturingAnalysisClient(LLMClient):
    def __init__(self):
        self.payloads = []
        self.prompts = []

    async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
        self.payloads.append(payload)
        self.prompts.append((system_prompt, user_prompt))
        if payload.get("mode") == "data_extraction":
            return {
                "data_points": [{"id": "dp-1", "name": "规模", "value": 10, "unit": "亿元", "year": 2024, "category": "market_size"}],
                "time_series": [],
                "distributions": [],
                "insights": ["规模保持增长"],
            }
        if payload.get("mode") == "knowledge_graph":
            return {"nodes": [{"id": "industry", "name": "行业", "type": "core", "importance": 8}], "edges": []}
        return {
            "charts": [{
                "id": "chart-1",
                "title": "规模",
                "type": "bar",
                "data": {"data_point_ids": ["dp-1"]},
                "echarts_option": {"series": [{"type": "bar", "data": [10]}]},
            }]
        }

    async def complete_text(self, role, payload):
        return ""


class DataAnalystAgentTests(unittest.TestCase):
    def test_data_analyst_runs_reference_three_stage_pipeline(self):
        async def run():
            client = CapturingAnalysisClient()
            state = ResearchState("测试问题")
            state.facts = [{"content": "事实", "source_url": "https://example.com"}]
            await DataAnalystAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())
        self.assertEqual(
            [payload["mode"] for payload in client.payloads],
            ["data_extraction", "knowledge_graph", "chart_generation"],
        )
        self.assertEqual(len(state.knowledge_graph["nodes"]), 1)
        self.assertEqual(state.knowledge_graph["nodes"][0]["size"], 44)
        self.assertEqual(len(state.charts), 1)
        self.assertEqual(state.data_points[0]["category"], "market_size")
        self.assertIn("从以上搜索结果中提取所有可量化的数据点", client.prompts[0][1])
        self.assertIn("实体类型定义", client.prompts[1][1])
        self.assertIn("时间序列数据 → line (折线图)", client.prompts[2][1])
        self.assertIn("事实 (来源: 未知)", client.payloads[0]["search_results"])
        self.assertEqual(client.payloads[1]["content"], "事实")
        self.assertEqual(
            client.payloads[2]["data"]["existing_data_points"][0]["id"],
            "dp-1",
        )

    def test_data_analyst_replaces_fact_extractor_graph_like_reference(self):
        class GraphAnalysisClient(LLMClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                if payload["mode"] == "data_extraction":
                    return {
                        "data_points": [],
                        "time_series": [],
                        "distributions": [],
                        "insights": [],
                    }
                if payload["mode"] == "knowledge_graph":
                    return {
                        "nodes": [
                            {
                                "id": "analyst-existing",
                                "name": "已有实体",
                                "type": "company",
                                "importance": 9,
                            },
                            {
                                "id": "node_0",
                                "name": "新增实体",
                                "type": "product",
                                "importance": 7,
                            },
                        ],
                        "edges": [
                            {
                                "source": "analyst-existing",
                                "target": "node_0",
                                "relation": "推出",
                            }
                        ],
                    }
                raise AssertionError("没有结构化数据时不应请求图表生成")

            async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
                return ""

        state = ResearchState("测试问题")
        state.facts = [{"content": "已有实体发布新产品", "source_url": "https://example.com"}]
        state.knowledge_graph = {
            "nodes": [
                {
                    "id": "node_0",
                    "name": "已有实体",
                    "type": "industry",
                    "relations": ["受市场影响"],
                }
            ],
            "edges": [{"source": "已有实体", "relation": "受市场影响"}],
        }

        asyncio.run(DataAnalystAgent(GraphAnalysisClient()).run(state))

        nodes_by_name = {node["name"]: node for node in state.knowledge_graph["nodes"]}
        self.assertEqual(set(nodes_by_name), {"已有实体", "新增实体"})
        self.assertEqual(nodes_by_name["已有实体"]["type"], "company")
        self.assertNotIn("受市场影响", str(state.knowledge_graph))
        self.assertEqual(nodes_by_name["已有实体"]["size"], 47)
        self.assertEqual(nodes_by_name["新增实体"]["size"], 41)
        self.assertEqual(len(state.knowledge_graph["edges"]), 1)
        self.assertEqual(
            state.knowledge_graph["edges"][0],
            {
                "source": "analyst-existing",
                "target": "node_0",
                "relation": "推出",
            },
        )

    def test_data_analyst_generates_insights_and_echarts_config(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await DataAnalystAgent(CapturingAnalysisClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "analyzing")
        self.assertEqual(len(state.insights), 1)
        self.assertEqual(len(state.charts), 1)
        chart = state.charts[0]
        self.assertEqual(chart["chart_type"], "bar")
        self.assertEqual(chart["data"]["data_point_ids"], ["dp-1"])
        self.assertEqual(chart["echarts_option"]["series"][0]["type"], "bar")
        self.assertEqual(
            chart["echarts_option"]["series"][0]["data"],
            [10],
        )

    def test_data_analyst_appends_results_like_reference(self):
        async def run():
            state = ResearchState("测试问题")
            state.facts = [{"content": "事实", "source_url": "https://example.com"}]
            state.data_points = [
                {"id": "dp-1", "name": "指标", "value": 10, "year": 2024}
            ]
            agent = DataAnalystAgent(CapturingAnalysisClient())
            await agent.run(state)
            await agent.run(state)
            return state

        state = asyncio.run(run())

        self.assertEqual(len(state.insights), 2)
        self.assertEqual(len(state.charts), 2)

    def test_data_analyst_rejects_invalid_echarts_series(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
        state.data_points = [{"id": "dp-1", "name": "指标", "value": 1}]

        with self.assertRaisesRegex(ValueError, "series 必须是非空列表"):
            asyncio.run(DataAnalystAgent(InvalidAnalysisClient()).run(state))

    def test_data_analyst_allows_facts_without_data_points(self):
        async def run():
            class EmptyAnalysisClient(LLMClient):
                async def complete_json(self, role, payload):
                    if payload["mode"] == "data_extraction":
                        return {
                            "data_points": [],
                            "time_series": [],
                            "distributions": [],
                            "insights": [],
                        }
                    return {"nodes": [], "edges": []}

                async def complete_text(self, role, payload):
                    return ""

            state = ResearchState("测试问题")
            state.facts = [{"content": "定性事实", "source_url": "https://example.com"}]
            await DataAnalystAgent(EmptyAnalysisClient()).run(state)
            return state

        state = asyncio.run(run())

        self.assertEqual(state.phase, "analyzing")
        self.assertEqual(state.charts, [])

    def test_data_analyst_uses_reference_fact_limits_and_skips_chart_without_extracted_data(self):
        class EmptyAnalysisClient(CapturingAnalysisClient):
            async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
                self.payloads.append(payload)
                self.prompts.append((system_prompt, user_prompt))
                if payload["mode"] == "data_extraction":
                    return {"data_points": [], "time_series": [], "distributions": [], "insights": []}
                return {"nodes": [], "edges": []}

        state = ResearchState("测试问题")
        state.facts = [
            {"content": f"事实 {index}", "source_name": f"来源 {index}"}
            for index in range(25)
        ]
        state.data_points = [{"id": "existing", "name": "旧指标", "value": 1}]
        client = EmptyAnalysisClient()
        asyncio.run(DataAnalystAgent(client).run(state))

        self.assertEqual([item["mode"] for item in client.payloads], ["data_extraction", "knowledge_graph"])
        self.assertIn("事实 19", client.payloads[0]["search_results"])
        self.assertNotIn("事实 20", client.payloads[0]["search_results"])
        self.assertIn("事实 14", client.payloads[1]["content"])
        self.assertNotIn("事实 15", client.payloads[1]["content"])

    def test_data_analyst_preserves_period_year_labels(self):
        target = []
        DataAnalystAgent._append_structured_data_points(
            target,
            [
                {
                    "name": "累计用户",
                    "value": 100,
                    "year": "2016-2023",
                    "confidence": 0.8,
                },
                {
                    "name": "年度用户",
                    "value": 120,
                    "year": "2024",
                    "confidence": 0.8,
                },
            ],
        )

        self.assertIsNone(target[0]["year"])
        self.assertEqual(target[0]["year_label"], "2016-2023")
        self.assertEqual(target[1]["year"], 2024)


if __name__ == "__main__":
    unittest.main()
