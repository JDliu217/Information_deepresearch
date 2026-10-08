import asyncio
import unittest

from app.agents.critic import CriticAgent
from app.agents.data_analyst import DataAnalystAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.code_wizard import CodeWizardAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.graph.nodes import ResearchGraphNodes
from app.graph.state import initial_graph_state


class GraphNodeTests(unittest.TestCase):
    def setUp(self):
        llm = MockLLMClient()
        nodes = ResearchGraphNodes(
            planner=PlannerAgent(llm),
            researcher=ResearcherAgent(MockSearchClient()),
            fact_extractor=FactExtractorAgent(llm),
            data_analyst=DataAnalystAgent(llm),
            code_wizard=CodeWizardAgent(llm),
            writer=WriterAgent(llm),
            critic=CriticAgent(llm),
        )
        self.nodes = nodes

    def test_initial_graph_state_wraps_single_domain_state(self):
        state = ResearchState("测试问题")
        graph_state = initial_graph_state(state)

        self.assertIs(graph_state["research_state"], state)
        self.assertEqual(graph_state["events"], [])
        self.assertFalse(graph_state["supplementary"])

    def test_plan_node_updates_domain_state_and_emits_events(self):
        state = ResearchState("测试问题")

        graph_state = initial_graph_state(state)
        started = self.nodes.planning_started(graph_state)
        result = asyncio.run(self.nodes.plan(graph_state))

        self.assertFalse(state.outline)
        self.assertTrue(result["research_state"].outline)
        self.assertIsNot(result["research_state"], state)
        self.assertEqual(started["events"][0]["type"], "phase_started")
        self.assertEqual(started["events"][0]["phase"], "planning")
        self.assertEqual(result["events"][0]["type"], "outline_ready")

    def test_plan_node_stops_before_search_when_planner_cannot_validate_an_outline(self):
        class InvalidPlanner:
            name = "planner"

            async def run(self, state):
                state.errors.append("Failed to generate research plan after retries")
                return state

        nodes = ResearchGraphNodes(
            planner=InvalidPlanner(),
            researcher=self.nodes.researcher,
            fact_extractor=self.nodes.fact_extractor,
            data_analyst=self.nodes.data_analyst,
            code_wizard=self.nodes.code_wizard,
            writer=self.nodes.writer,
            critic=self.nodes.critic,
        )

        with self.assertRaisesRegex(ValueError, "停止后续搜索"):
            asyncio.run(nodes.plan(initial_graph_state(ResearchState("测试问题"))))

    def test_extract_facts_consumes_supplementary_flag_after_emitting_event(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "补充来源",
                "url": "https://example.com/supplementary",
                "source": "测试站点",
                "summary": "补充摘要",
            }
        ]

        result = asyncio.run(
            self.nodes.extract_facts(
                {
                    **initial_graph_state(state),
                    "supplementary": True,
                }
            )
        )

        self.assertFalse(result["supplementary"])
        self.assertTrue(result["events"][0]["supplementary"])

    def test_extract_facts_passes_reference_analysis_mode_to_agent(self):
        class RecordingFactExtractor:
            name = "FactExtractorAgent"

            def __init__(self):
                self.modes = []

            async def run(self, state, *, mode):
                self.modes.append(mode)
                return state

        recorder = RecordingFactExtractor()
        nodes = ResearchGraphNodes(
            planner=self.nodes.planner,
            researcher=self.nodes.researcher,
            fact_extractor=recorder,
            data_analyst=self.nodes.data_analyst,
            code_wizard=self.nodes.code_wizard,
            writer=self.nodes.writer,
            critic=self.nodes.critic,
        )
        cases = [
            ({}, "normal"),
            ({"supplementary": True}, "supplementary"),
            ({"supplementary": True, "research_depth": 1}, "recursive"),
            # Depth remains in graph state after a recursive round. A later
            # planned section is normal research once the supplementary flag
            # has been consumed.
            ({"supplementary": False, "research_depth": 1}, "normal"),
        ]

        for graph_fields, _expected in cases:
            asyncio.run(
                nodes.extract_facts(
                    {
                        **initial_graph_state(ResearchState("测试问题")),
                        **graph_fields,
                    }
                )
            )

        self.assertEqual([mode for _, mode in cases], recorder.modes)


if __name__ == "__main__":
    unittest.main()
