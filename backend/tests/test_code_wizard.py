import asyncio
import unittest

from app.agents.code_wizard import CodeWizardAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.models import CodeExecution
from app.domain.state import ResearchState


def add_three_data_points(state: ResearchState) -> None:
    state.data_points = [
        {"id": f"dp-{index}", "name": f"指标 {index}", "value": index * 10, "unit": "亿元", "year": 2020 + index}
        for index in range(1, 4)
    ]


class DuplicateChartIdClient(MockLLMClient):
    async def complete_json(self, role, payload):
        if role == "code_wizard" and payload.get("mode") != "repair":
            return {
                "analysis_plan": "统计数据点数量。",
                "code": "result = {'count': len(data_points)}\nprint(result)",
                "expected_outputs": ["count"],
                "chart_ids": ["chart-1", "chart-1"],
            }
        return await super().complete_json(role, payload)


class UnknownChartIdClient(DuplicateChartIdClient):
    async def complete_json(self, role, payload):
        result = await super().complete_json(role, payload)
        if role == "code_wizard" and payload.get("mode") != "repair":
            result["chart_ids"] = ["missing-chart"]
        return result


class RepairingCodeWizardClient(MockLLMClient):
    async def complete_json(self, role, payload):
        if role == "code_wizard" and payload.get("mode") != "repair":
            return {
                "analysis_plan": "统计数据点数量。",
                "code": "result = {'count': 1 / 0}",
                "expected_outputs": ["count"],
            }
        return await super().complete_json(role, payload)


class AlwaysFailingCodeWizardClient(LLMClient):
    async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
        if payload.get("mode") == "repair":
            return {
                "fixed_code": "result = {'count': 1 / 0}",
                "error_analysis": "持续出现除零错误。",
                "fix_description": "仍然返回失败代码，用于测试重试上限。",
            }
        return {
            "analysis_plan": "统计数据点。",
            "code": "result = {'count': 1 / 0}",
            "expected_outputs": ["count"],
        }

    async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
        return ""


class CapturingRepairClient(RepairingCodeWizardClient):
    def __init__(self):
        self.repair_payloads = []

    async def complete_json(self, role, payload):
        if role == "code_wizard" and payload.get("mode") == "repair":
            self.repair_payloads.append(payload)
        return await super().complete_json(role, payload)


class FailingThenSucceedingExecutor:
    def __init__(self):
        self.calls = 0

    def execute(self, code, context, execution_id="exec_1"):
        self.calls += 1
        if self.calls == 1:
            return CodeExecution(
                id=execution_id,
                code=code,
                status="failed",
                stdout="x" * 1500,
                error="测试执行失败",
            )
        return CodeExecution(
            id=execution_id,
            code=code,
            status="succeeded",
            stdout="ok",
            result={"count": len(context["data_points"])},
        )


class CodeWizardAgentTests(unittest.TestCase):
    def test_restricted_executor_gets_a_prompt_for_its_supported_syntax(self):
        class CapturingPromptClient(MockLLMClient):
            def __init__(self):
                self.system_prompt = ""
                self.user_prompt = ""

            async def complete_json(
                self,
                role,
                payload,
                system_prompt="",
                user_prompt="",
                temperature=None,
                max_tokens=None,
            ):
                self.system_prompt = system_prompt
                self.user_prompt = user_prompt
                return await super().complete_json(role, payload)

        client = CapturingPromptClient()
        state = ResearchState("研究问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(client).run(state))

        self.assertIn("受限统计解释器", client.system_prompt)
        self.assertIn("numeric_values(data_points)", client.user_prompt)
        self.assertNotIn("pd.DataFrame", client.user_prompt)
        # Keep the original Python/pandas prompt available for a future
        # isolated runner that supports the reference execution contract.
        self.assertIn("pd.DataFrame", CodeWizardAgent.ANALYSIS_PROMPT)

    def test_code_wizard_executes_generated_plan_and_records_result(self):
        async def run():
            state = ResearchState("新能源汽车行业的数据趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            # The reference CodeWizard runs only when at least three data
            # points exist; this fixture exercises its execution path.
            add_three_data_points(state)
            state.outline = []
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

    def test_analysis_prompt_formats_metric_value_unit_and_year(self):
        class CapturingClient(MockLLMClient):
            def __init__(self):
                self.last_payload = None

            async def complete_json(self, role, payload):
                if role == "code_wizard":
                    self.last_payload = payload
                return await super().complete_json(role, payload)

        client = CapturingClient()
        state = ResearchState("研究问题")
        add_three_data_points(state)
        asyncio.run(CodeWizardAgent(client).run(state))

        self.assertIn("- 指标 1: 10 亿元 (2021)", client.last_payload["data_summary"])
        self.assertIn("- 指标 3: 30 亿元 (2023)", client.last_payload["data_summary"])

    def test_analysis_is_skipped_until_three_data_points_exist(self):
        class CountingClient(MockLLMClient):
            calls = 0

            async def complete_json(self, role, payload):
                self.calls += 1
                return await super().complete_json(role, payload)

        client = CountingClient()
        state = ResearchState("只有两个数据点")
        state.data_points = [{"name": "A", "value": 1}, {"name": "B", "value": 2}]

        asyncio.run(CodeWizardAgent(client).run(state))

        self.assertEqual(client.calls, 0)
        self.assertEqual(state.code_executions, [])

    def test_code_wizard_deduplicates_legacy_chart_ids_and_associates_chart(self):
        state = ResearchState("测试问题")
        add_three_data_points(state)
        state.charts = [{"id": "chart-1", "title": "测试图表"}]

        asyncio.run(CodeWizardAgent(DuplicateChartIdClient()).run(state))

        self.assertEqual(state.code_executions[0]["chart_ids"], ["chart-1"])
        self.assertEqual(state.charts[0]["execution_id"], "exec_1")
        self.assertEqual(state.charts[0]["code"], state.code_executions[0]["code"])

    def test_code_wizard_ignores_unknown_legacy_chart_ids(self):
        state = ResearchState("测试问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(UnknownChartIdClient()).run(state))

        self.assertEqual(state.code_executions[0]["chart_ids"], [])
        self.assertEqual(state.code_executions[0]["status"], "succeeded")

    def test_code_wizard_tolerates_non_list_expected_outputs_metadata(self):
        class CompatibleModelClient(MockLLMClient):
            async def complete_json(self, role, payload, **kwargs):
                if role == "code_wizard" and payload.get("mode") != "repair":
                    return {
                        "analysis_plan": "统计数据点数量。",
                        "code": "result = {'count': len(data_points)}\nprint(result)",
                        "expected_outputs": {"description": "统计结果"},
                    }
                return await super().complete_json(role, payload, **kwargs)

        state = ResearchState("测试问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(CompatibleModelClient()).run(state))

        self.assertEqual(state.code_executions[0]["status"], "succeeded")
        self.assertEqual(
            state.code_executions[0]["result"]["expected_outputs"],
            ["统计结果"],
        )

    def test_rejected_code_is_not_sent_back_for_repair(self):
        class UnsafeCodeClient(MockLLMClient):
            calls = 0

            async def complete_json(self, role, payload):
                if role == "code_wizard":
                    self.calls += 1
                    return {
                        "analysis_plan": "尝试执行不安全代码。",
                        "code": "import os",
                        "expected_outputs": [],
                    }
                return await super().complete_json(role, payload)

        client = UnsafeCodeClient()
        state = ResearchState("测试问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(client).run(state))

        self.assertEqual(client.calls, 1)
        self.assertEqual(state.code_executions[0]["status"], "rejected")


    def test_code_wizard_skips_analysis_with_fewer_than_three_data_points(self):
        state = ResearchState("定性问题")
        state.data_points = [{"id": "dp-1", "name": "指标", "value": 1}]

        result = asyncio.run(CodeWizardAgent(MockLLMClient()).run(state))

        self.assertIs(result, state)
        self.assertEqual(state.code_executions, [])

    def test_code_wizard_repairs_runtime_failure_once(self):
        state = ResearchState("测试问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(RepairingCodeWizardClient()).run(state))

        self.assertEqual([item["status"] for item in state.code_executions], ["failed", "succeeded"])
        self.assertIn("data_point_count", state.code_executions[1]["code"])
        self.assertEqual(state.code_executions[1]["result"]["output"]["data_point_count"], 3)

    def test_repair_feedback_stdout_is_limited_to_1000_characters(self):
        client = CapturingRepairClient()
        state = ResearchState("测试问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(client, FailingThenSucceedingExecutor()).run(state))

        self.assertEqual(len(client.repair_payloads), 1)
        self.assertEqual(len(client.repair_payloads[0]["stdout"]), 1000)
        fixed = CodeWizardAgent._validate_fix(
            {
                "fixed_code": "print('ok')",
                "error_analysis": "原因",
                "fix_description": "修复",
            }
        )
        self.assertEqual(fixed["fixed_code"], "print('ok')")

    def test_code_wizard_limits_self_correction_to_three_repairs(self):
        state = ResearchState("测试问题")
        add_three_data_points(state)

        asyncio.run(CodeWizardAgent(AlwaysFailingCodeWizardClient()).run(state))

        self.assertEqual(len(state.code_executions), 4)
        self.assertTrue(all(item["status"] == "failed" for item in state.code_executions))

    def test_chart_selection_and_section_context_follow_reference_limits(self):
        state = ResearchState("章节图表")
        state.outline = [
            {"id": f"sec_{index}", "title": f"章节 {index}", "requires_chart": True}
            for index in range(1, 5)
        ]
        state.facts = [
            {
                "related_sections": ["sec_1"],
                "data_points": [{"id": "related", "name": "章节指标", "value": 99}],
            }
        ]
        state.data_points = [
            {"id": f"global-{index}", "name": f"全局指标 {index}", "value": index}
            for index in range(12)
        ]
        agent = CodeWizardAgent(MockLLMClient())

        selected = agent._select_chart_sections(state.outline)
        section_data = agent._section_data(state, "sec_1")

        self.assertEqual([section["id"] for section in selected], ["sec_1", "sec_2"])
        self.assertEqual(len(section_data), 11)
        self.assertEqual(section_data[0]["id"], "related")
        self.assertEqual(section_data[-1]["id"], "global-9")

    def test_chart_fallback_uses_first_two_sections(self):
        outline = [{"id": f"sec_{index}"} for index in range(1, 5)]

        selected = CodeWizardAgent._select_chart_sections(outline)

        self.assertEqual([section["id"] for section in selected], ["sec_1", "sec_2"])

    def test_chart_generation_receives_related_and_first_ten_global_points(self):
        class CapturingChartClient(MockLLMClient):
            def __init__(self):
                self.chart_payloads = []

            async def complete_json(self, role, payload):
                if role == "code_wizard" and payload.get("mode") == "chart_generation":
                    self.chart_payloads.append(payload)
                return await super().complete_json(role, payload)

        client = CapturingChartClient()
        state = ResearchState("章节图表")
        state.outline = [{"id": "sec_1", "title": "第一章", "requires_chart": True}]
        state.facts = [
            {
                "related_sections": ["sec_1"],
                "data_points": [{"id": "related", "name": "章节指标", "value": 99}],
            }
        ]
        state.data_points = [
            {"id": f"global-{index}", "name": f"全局指标 {index}", "value": index}
            for index in range(12)
        ]

        asyncio.run(CodeWizardAgent(client).run(state))

        self.assertEqual(len(client.chart_payloads), 1)
        data = client.chart_payloads[0]["data"]
        self.assertEqual(len(data), 11)
        self.assertEqual(data[0]["id"], "related")
        self.assertEqual(data[-1]["id"], "global-9")

    def test_chart_rendering_limit_applies_after_generating_code_for_two_sections(self):
        state = ResearchState("章节图表")
        state.outline = [
            {"id": "sec_1", "title": "第一章", "requires_chart": True},
            {"id": "sec_2", "title": "第二章", "requires_chart": True},
            {"id": "sec_3", "title": "第三章", "requires_chart": True},
        ]
        state.data_points = [{"id": f"dp-{i}", "name": "指标", "value": i} for i in range(1, 4)]

        asyncio.run(CodeWizardAgent(MockLLMClient()).run(state))

        self.assertEqual(len(state.logs), 2)
        self.assertEqual([item["section_id"] for item in state.logs], ["sec_1", "sec_2"])
        self.assertIn("不支持", state.logs[0]["reason"])
        # Reference CodeWizard does not add a second CodeExecution record for
        # chart attempts; it only appends a chart when image rendering works.
        self.assertEqual(len(state.code_executions), 1)
        self.assertTrue(all(item["code"] for item in state.logs))


if __name__ == "__main__":
    unittest.main()
