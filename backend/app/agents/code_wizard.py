"""CodeWizard 的代码生成阶段。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState
from app.execution.restricted_executor import RestrictedCodeExecutor

from .base import BaseAgent


class CodeWizardAgent(BaseAgent):
    """为数据分析生成待执行代码，并记录执行前的计划。"""

    name = "code_wizard"
    ANALYSIS_SYSTEM = """你是 DeepResearch 的 CodeWizard。代码会在严格受限执行器中运行，不能 import、
访问网络、文件、进程、属性链或动态执行，只能使用输入中的 data_points、facts、insights 和 charts。
不要编造数据或图表 ID。"""
    ANALYSIS_PROMPT = """请根据已有数据点生成短小的受控统计分析代码。返回 purpose、code、expected_outputs
和 chart_ids。代码只做必要的计数、均值、最小值、最大值或趋势摘要。"""
    CODE_FIX_PROMPT = """请根据受控执行器返回的错误修复代码。保持原分析目的和已有图表 ID，不增加
import、文件、网络、进程或动态执行。"""
    CHART_CODE_PROMPT = """请为已有图表生成与数据点一致的受控代码，不能引用不存在的图表 ID。"""

    def __init__(
        self,
        llm: LLMClient,
        executor: RestrictedCodeExecutor | None = None,
    ):
        self.llm = llm
        self.executor = executor or RestrictedCodeExecutor()

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.facts:
            raise ValueError("没有可供 CodeWizard 分析的事实")
        if not state.data_points:
            return state

        payload = {
            "query": state.query,
            "facts": state.facts,
            "data_points": state.data_points,
            "insights": state.insights,
            "charts": state.charts,
            "instruction": (
                "只根据已有事实和数据点生成分析代码。代码将在受控执行器中运行，"
                "不要访问网络、文件系统或进程；返回代码用途、预期输出和关联图表 ID。"
            ),
        }
        result = await self._complete_json(
            payload,
            system_prompt=self.ANALYSIS_SYSTEM,
            user_prompt=self._render_prompt(self.ANALYSIS_PROMPT, payload),
        )
        plan = self._validate_plan(result)
        known_chart_ids = {str(chart.get("id", "")).strip() for chart in state.charts}
        unknown_chart_ids = set(plan["chart_ids"]) - known_chart_ids
        if unknown_chart_ids:
            raise ValueError("CodeWizard 引用了不存在的图表 ID")
        for attempt in range(2):
            execution = self.executor.execute(
                plan["code"],
                {
                    "data_points": state.data_points,
                    "facts": state.facts,
                    "insights": state.insights,
                    "charts": state.charts,
                },
                execution_id=f"exec_{len(state.code_executions) + 1}",
            )
            execution.result = {
                "purpose": plan["purpose"],
                "expected_outputs": plan["expected_outputs"],
                "output": execution.result,
            }
            execution.chart_ids = plan["chart_ids"]
            state.code_executions.append(execution.to_dict())
            if execution.status == "succeeded":
                for chart in state.charts:
                    if str(chart.get("id", "")).strip() in execution.chart_ids:
                        chart["code"] = execution.code
                        chart["execution_id"] = execution.id
            if execution.status != "failed" or attempt == 1:
                break
            repair_payload = {
                "mode": "repair",
                "query": state.query,
                "data_points": state.data_points,
                "code": plan["code"],
                "error": execution.error,
                "instruction": "修复运行错误，保持相同的分析目的和图表 ID。",
            }
            repaired = await self._complete_json(
                repair_payload,
                system_prompt=self.ANALYSIS_SYSTEM,
                user_prompt=self._render_prompt(self.CODE_FIX_PROMPT, repair_payload),
            )
            repaired_plan = self._validate_plan(repaired)
            if set(repaired_plan["chart_ids"]) - known_chart_ids:
                raise ValueError("CodeWizard 修复代码引用了不存在的图表 ID")
            plan = repaired_plan
        state.phase = "analyzing"
        return state

    @staticmethod
    def _validate_plan(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("CodeWizard 返回结果必须是对象")

        code = str(value.get("code", "")).strip()
        if not code:
            raise ValueError("CodeWizard 返回结果缺少 code")

        purpose = str(value.get("purpose", "")).strip()
        if not purpose:
            raise ValueError("CodeWizard 返回结果缺少 purpose")

        expected_outputs = value.get("expected_outputs", [])
        if not isinstance(expected_outputs, list) or not all(
            isinstance(item, str) and item.strip() for item in expected_outputs
        ):
            raise ValueError("CodeWizard expected_outputs 必须是字符串列表")

        chart_ids = value.get("chart_ids", [])
        if not isinstance(chart_ids, list) or not all(
            isinstance(item, str) and item.strip() for item in chart_ids
        ):
            raise ValueError("CodeWizard chart_ids 必须是字符串列表")

        normalized_chart_ids = [item.strip() for item in chart_ids]
        if len(normalized_chart_ids) != len(set(normalized_chart_ids)):
            raise ValueError("CodeWizard chart_ids 不能重复")

        return {
            "code": code,
            "purpose": purpose,
            "expected_outputs": [item.strip() for item in expected_outputs],
            "chart_ids": normalized_chart_ids,
        }
