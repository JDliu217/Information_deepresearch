"""CodeWizard 的代码生成阶段。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import CodeExecution
from app.domain.state import ResearchState

from .base import BaseAgent


class CodeWizardAgent(BaseAgent):
    """为数据分析生成待执行代码，并记录执行前的计划。"""

    name = "code_wizard"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.facts:
            raise ValueError("没有可供 CodeWizard 分析的事实")
        if not state.data_points:
            raise ValueError("没有可供 CodeWizard 分析的数据点")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "facts": state.facts,
                "data_points": state.data_points,
                "insights": state.insights,
                "charts": state.charts,
                "instruction": (
                    "只根据已有事实和数据点生成分析代码。代码将在受控执行器中运行，"
                    "不要访问网络、文件系统或进程；返回代码用途、预期输出和关联图表 ID。"
                ),
            },
        )
        plan = self._validate_plan(result)
        execution = CodeExecution(
            id=f"exec_{len(state.code_executions) + 1}",
            code=plan["code"],
            result={
                "purpose": plan["purpose"],
                "expected_outputs": plan["expected_outputs"],
            },
            chart_ids=plan["chart_ids"],
        )
        state.code_executions.append(execution.to_dict())
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
