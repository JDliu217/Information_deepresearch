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


class SixSectionLLM(MockLLMClient):
    async def complete_json(self, role, payload):
        if role == "planner":
            return {
                "outline": [
                    {
                        "id": f"sec_{index}",
                        "title": f"章节 {index}",
                        "description": f"描述 {index}",
                        "search_queries": [f"查询 {index}"],
                    }
                    for index in range(1, 7)
                ],
                "research_questions": [f"问题 {index}" for index in range(1, 7)],
                "hypotheses": [],
                "key_entities": [],
            }
        return await super().complete_json(role, payload)


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
    def test_graph_researches_all_sections_in_three_section_batches(self):
        llm = SixSectionLLM()
        graph = build_research_graph(
            ResearchGraphNodes(
                planner=PlannerAgent(llm),
                researcher=ResearcherAgent(MockSearchClient()),
                fact_extractor=FactExtractorAgent(llm),
                data_analyst=DataAnalystAgent(llm),
                code_wizard=CodeWizardAgent(llm),
                writer=WriterAgent(llm),
                critic=CriticAgent(llm),
            )
        )

        result = asyncio.run(
            graph.ainvoke(initial_graph_state(ResearchState("六章节问题")))
        )

        state = result["research_state"]
        self.assertEqual(len(state.raw_sources), 6)
        self.assertEqual(len(state.facts), 6)
        self.assertEqual({fact["section_id"] for fact in state.facts}, {f"sec_{i}" for i in range(1, 7)})
        self.assertTrue(all(section["status"] == "drafted" for section in state.outline))

    def test_linear_graph_runs_existing_agents_in_order(self):
        graph = build_research_graph(make_nodes())
        state = ResearchState("测试问题")

        result = asyncio.run(graph.ainvoke(initial_graph_state(state)))

        self.assertIsNot(result["research_state"], state)
        self.assertEqual(state.phase, "init")
        self.assertEqual(result["research_state"].phase, "completed")
        self.assertTrue(result["research_state"].final_report)
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
