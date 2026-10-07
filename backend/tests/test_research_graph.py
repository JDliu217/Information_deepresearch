import asyncio
import unittest

from app.agents.code_wizard import CodeWizardAgent
from app.agents.critic import CriticAgent
from app.agents.data_analyst import DataAnalystAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.graph.nodes import ResearchGraphNodes
from app.graph.research_graph import build_research_graph
from app.graph.state import initial_graph_state


def make_nodes() -> ResearchGraphNodes:
    llm = MockLLMClient()
    return ResearchGraphNodes(
        planner=PlannerAgent(llm),
        researcher=ResearcherAgent(MockSearchClient()),
        fact_extractor=FactExtractorAgent(llm),
        data_analyst=DataAnalystAgent(llm),
        code_wizard=CodeWizardAgent(llm),
        writer=WriterAgent(llm),
        critic=CriticAgent(llm),
    )


class ResearchGraphTests(unittest.TestCase):
    def test_linear_graph_runs_existing_agents_in_order(self):
        graph = build_research_graph(make_nodes())
        state = ResearchState("测试问题")

        result = asyncio.run(graph.ainvoke(initial_graph_state(state)))

        self.assertEqual(result["research_state"], state)
        self.assertEqual(state.phase, "completed")
        self.assertTrue(state.final_report)
        self.assertEqual(
            [event["type"] for event in result["events"]],
            [
                "research_started",
                "phase_started",
                "outline_ready",
                "phase_started",
                "research_evidence_ready",
                "phase_started",
                "analysis_ready",
                "phase_started",
                "draft_ready",
                "phase_started",
                "review_completed",
                "research_completed",
            ],
        )


if __name__ == "__main__":
    unittest.main()
