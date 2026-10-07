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


class CodeWizardAgentTests(unittest.TestCase):
    def test_code_wizard_records_pending_plan_without_executing_code(self):
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
        self.assertEqual(execution["status"], "pending")
        self.assertIn("data_point_count", execution["code"])
        self.assertEqual(execution["stdout"], "")

    def test_code_wizard_rejects_duplicate_chart_ids(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
        state.data_points = [{"id": "dp-1", "name": "指标", "value": 1}]

        with self.assertRaisesRegex(ValueError, "chart_ids 不能重复"):
            asyncio.run(CodeWizardAgent(InvalidCodeWizardClient()).run(state))


if __name__ == "__main__":
    unittest.main()
