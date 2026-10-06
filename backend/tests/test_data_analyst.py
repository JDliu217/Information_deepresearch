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


class DataAnalystAgentTests(unittest.TestCase):
    def test_data_analyst_generates_insights_and_echarts_config(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await DataAnalystAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "analyzing")
        self.assertEqual(len(state.insights), 1)
        self.assertEqual(len(state.charts), 1)
        chart = state.charts[0]
        self.assertEqual(chart["chart_type"], "bar")
        self.assertEqual(chart["data"]["data_point_ids"], ["dp_1", "dp_2", "dp_3"])
        self.assertEqual(chart["echarts_option"]["series"][0]["type"], "bar")
        self.assertEqual(
            chart["echarts_option"]["series"][0]["data"],
            [10, 20, 30],
        )

    def test_data_analyst_upserts_same_chart_and_deduplicates_insight(self):
        async def run():
            state = ResearchState("测试问题")
            state.facts = [{"content": "事实", "source_url": "https://example.com"}]
            state.data_points = [
                {"id": "dp-1", "name": "指标", "value": 10, "year": 2024}
            ]
            agent = DataAnalystAgent(MockLLMClient())
            await agent.run(state)
            await agent.run(state)
            return state

        state = asyncio.run(run())

        self.assertEqual(len(state.insights), 1)
        self.assertEqual(len(state.charts), 1)

    def test_data_analyst_rejects_invalid_echarts_series(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]

        with self.assertRaisesRegex(ValueError, "series 必须是非空列表"):
            asyncio.run(DataAnalystAgent(InvalidAnalysisClient()).run(state))

    def test_data_analyst_allows_facts_without_data_points(self):
        async def run():
            state = ResearchState("测试问题")
            state.facts = [{"content": "定性事实", "source_url": "https://example.com"}]
            await DataAnalystAgent(MockLLMClient()).run(state)
            return state

        state = asyncio.run(run())

        self.assertEqual(state.phase, "analyzing")
        self.assertEqual(state.insights, [])
        self.assertEqual(state.charts, [])


if __name__ == "__main__":
    unittest.main()
