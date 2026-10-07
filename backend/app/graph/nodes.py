"""把现有 Agent 包装成 LangGraph 节点。

节点只负责调用 Agent 和生成稳定的 ``ResearchEvent``。路由判断会在
后续文件中单独实现，这样节点不会同时承担流程控制职责。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from app.agents.code_wizard import CodeWizardAgent
from app.agents.critic import CriticAgent
from app.agents.data_analyst import DataAnalystAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.domain.events import ResearchEvent

from .routes import prepare_review_route
from .state import ResearchGraphState


@dataclass(frozen=True)
class ResearchGraphNodes:
    """已有 Agent 的节点适配器。

    ``ResearchWorkflow`` 创建 Agent 实例后，将它们传入这里。这样 I7
    不会复制或重写任何 Agent 业务逻辑。
    """

    planner: PlannerAgent
    researcher: ResearcherAgent
    fact_extractor: FactExtractorAgent
    data_analyst: DataAnalystAgent
    code_wizard: CodeWizardAgent
    writer: WriterAgent
    critic: CriticAgent

    async def start(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = graph_state["research_state"]
        return {
            "events": [
                self._event(
                    state,
                    "research_started",
                    query=state.query,
                    max_iterations=state.max_iterations,
                )
            ]
        }

    async def plan(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        events = [self._event(state, "phase_started", phase="planning", agent=self.planner.name)]
        await self.planner.run(state)
        events.append(
            self._event(
                state,
                "outline_ready",
                outline=state.outline,
                research_questions=state.research_questions,
                hypotheses=state.hypotheses,
                key_entities=state.key_entities,
                mind_map=state.mind_map,
            )
        )
        return {"research_state": state, "events": events}

    async def research(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        supplementary = bool(graph_state.get("supplementary", False))
        await self.researcher.run(state)
        return {
            "research_state": state,
            "events": [
                self._event(
                    state,
                    "phase_started",
                    phase="researching",
                    agent=self.researcher.name,
                    supplementary=supplementary,
                )
            ],
        }

    async def extract_facts(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        supplementary = bool(graph_state.get("supplementary", False))
        await self.fact_extractor.run(state)
        return {
            "research_state": state,
            "events": [
                self._event(
                    state,
                    "research_evidence_ready",
                    supplementary=supplementary,
                    source_count=len(state.raw_sources),
                    fact_count=len(state.facts),
                    sources=state.raw_sources,
                    facts=state.facts,
                    references=state.references,
                )
            ]
        }

    async def analyze(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        event = self._event(
            state,
            "phase_started",
            phase="analyzing",
            agent=self.data_analyst.name,
        )
        await self.data_analyst.run(state)
        return {
            "research_state": state,
            "events": [event],
        }

    async def execute_analysis(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        await self.code_wizard.run(state)
        return {
            "research_state": state,
            "events": [
                self._event(
                    state,
                    "analysis_ready",
                    insights=state.insights,
                    data_points=state.data_points,
                    charts=state.charts,
                    code_executions=state.code_executions,
                    insight_count=len(state.insights),
                    chart_count=len(state.charts),
                    code_execution_count=len(state.code_executions),
                )
            ]
        }

    async def write(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        revision = bool(graph_state.get("revision", False))
        events = [
            self._event(
                state,
                "phase_started",
                phase="writing",
                agent=self.writer.name,
                revision=revision,
            )
        ]
        await self.writer.run(state)
        events.append(
            self._event(
                state,
                "draft_ready",
                report=state.final_report,
                outline=state.outline,
                draft_sections=state.draft_sections,
                revision=revision,
            )
        )
        return {"research_state": state, "events": events}

    async def review(self, graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        events = [
            self._event(state, "phase_started", phase="reviewing", agent=self.critic.name)
        ]
        await self.critic.run(state)
        events.append(
            self._event(
                state,
                "review_completed",
                review_result=state.review_result,
                critic_feedback=state.critic_feedback,
                quality_score=state.quality_score,
                unresolved_issues=state.unresolved_issues,
                fact_check_results=state.review_result.get("fact_check_results", []),
                missing_aspects=state.review_result.get("missing_aspects", []),
                strengths=state.review_result.get("strengths", []),
            )
        )
        return {"research_state": state, "events": events}

    @staticmethod
    def route_review(graph_state: ResearchGraphState) -> dict[str, Any]:
        """执行审核后的状态更新；具体条件边由 ``routes`` 负责读取。"""

        return prepare_review_route(graph_state)

    @staticmethod
    def complete(graph_state: ResearchGraphState) -> dict[str, Any]:
        state = deepcopy(graph_state["research_state"])
        state.phase = "completed"
        return {
            "research_state": state,
            "events": [
                ResearchGraphNodes._event(
                    state,
                    "research_completed",
                    report=state.final_report,
                    quality_score=state.quality_score,
                    references=state.references,
                    review_result=state.review_result,
                    critic_feedback=state.critic_feedback,
                    unresolved_issues=state.unresolved_issues,
                    fact_check_results=state.review_result.get("fact_check_results", []),
                    missing_aspects=state.review_result.get("missing_aspects", []),
                    strengths=state.review_result.get("strengths", []),
                    insights=state.insights,
                    data_points=state.data_points,
                    charts=state.charts,
                    code_executions=state.code_executions,
                )
            ]
        }

    @staticmethod
    def _event(
        state: Any,
        event_type: str,
        *,
        phase: str | None = None,
        **data: Any,
    ) -> dict[str, Any]:
        return ResearchEvent(
            type=event_type,
            session_id=state.session_id,
            phase=phase or state.phase,
            iteration=state.iteration,
            data=data,
        ).to_dict()
