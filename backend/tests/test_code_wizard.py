import asyncio
import unittest

from app.agents.code_wizard import CodeWizardAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class InvalidCodeWizardClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "purpose": "无效计划",
            "code": "print('ok')",
            "expected_outputs": ["summary"],
            "chart_ids": ["chart-1", "chart-1"],
        }

    async def complete_text(self, role, payload):
        return ""


class UnknownChartClient(InvalidCodeWizardClient):
    async def complete_json(self, role, payload):
        result = await super().complete_json(role, payload)
        result["chart_ids"] = ["missing-chart"]
        return result


class CodeWizardAgentTests(unittest.TestCase):
    def test_code_wizard_executes_generated_plan_and_records_result(self):
        async def run():
            state = ResearchState("新能源汽车行业的数据趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await CodeWizardAgent(llm).run(state)
            return state

        state = asyncio.run(run())

        self.assertEqual(len(state.code_executions), 1)
        execution = state.code_executions[0]
        self.assertEqual(execution["id"], "exec_1")
        self.assertEqual(execution["status"], "succeeded")
        self.assertIn("data_point_count", execution["code"])
        self.assertEqual(execution["result"]["output"]["data_point_count"], 3)
        self.assertIn("data_point_count", execution["stdout"])

    def test_code_wizard_rejects_duplicate_chart_ids(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
        state.data_points = [{"id": "dp-1", "name": "指标", "value": 1}]

        with self.assertRaisesRegex(ValueError, "chart_ids 不能重复"):
            asyncio.run(CodeWizardAgent(InvalidCodeWizardClient()).run(state))

    def test_code_wizard_rejects_unknown_chart_ids(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
        state.data_points = [{"id": "dp-1", "name": "指标", "value": 1}]

        with self.assertRaisesRegex(ValueError, "不存在的图表"):
            asyncio.run(CodeWizardAgent(UnknownChartClient()).run(state))

    def test_code_wizard_skips_qualitative_research_without_data_points(self):
        state = ResearchState("定性问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]

        result = asyncio.run(CodeWizardAgent(MockLLMClient()).run(state))

        self.assertIs(result, state)
        self.assertEqual(state.code_executions, [])


if __name__ == "__main__":
    unittest.main()
