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

        result = asyncio.run(self.nodes.plan(initial_graph_state(state)))

        self.assertFalse(state.outline)
        self.assertTrue(result["research_state"].outline)
        self.assertIsNot(result["research_state"], state)
        self.assertEqual([event["type"] for event in result["events"]], [
            "phase_started",
            "outline_ready",
        ])
        self.assertEqual(result["events"][0]["phase"], "planning")


if __name__ == "__main__":
    unittest.main()
