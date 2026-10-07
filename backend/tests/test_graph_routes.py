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
from app.graph.routes import prepare_review_route, select_review_route
from app.graph.state import initial_graph_state


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)


class GraphRecordingSearchClient(MockSearchClient):
    def __init__(self):
        self.queries = []

    async def search(self, query, limit=3):
        self.queries.append(query)
        return await super().search(query, limit)


def make_nodes(llm, search):
    return ResearchGraphNodes(
        planner=PlannerAgent(llm),
        researcher=ResearcherAgent(search),
        fact_extractor=FactExtractorAgent(llm),
        data_analyst=DataAnalystAgent(llm),
        code_wizard=CodeWizardAgent(llm),
        writer=WriterAgent(llm),
        critic=CriticAgent(llm),
    )


class GraphRouteTests(unittest.TestCase):
    def test_route_increments_iteration_and_prepares_supplementary_query(self):
        state = ResearchState("测试问题", max_iterations=1)
        state.review_result = review(
            "needs_revision",
            more_research=True,
            search_queries=["最新数据"],
        )

        result = prepare_review_route(initial_graph_state(state))

        self.assertEqual(result["route"], "research")
        self.assertTrue(result["supplementary"])
        self.assertEqual(state.iteration, 0)
        self.assertEqual(result["research_state"].iteration, 1)
        self.assertEqual(result["research_state"].pending_search_queries, ["最新数据"])
        self.assertEqual(select_review_route({**initial_graph_state(state), **result}), "research")

    def test_route_stops_when_max_iterations_is_reached(self):
        state = ResearchState("测试问题", max_iterations=1)
        state.iteration = 1
        state.review_result = review("needs_revision")

        result = prepare_review_route(initial_graph_state(state))

        self.assertEqual(result["route"], "stop")
        self.assertEqual(state.iteration, 1)

    def test_graph_loops_through_supplementary_research(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    search_queries=["最新数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = GraphRecordingSearchClient()
        graph = build_research_graph(make_nodes(llm, search))
        state = ResearchState("测试问题", max_iterations=1)

        result = asyncio.run(graph.ainvoke(initial_graph_state(state)))

        self.assertEqual(state.phase, "init")
        self.assertEqual(result["research_state"].phase, "completed")
        self.assertEqual(result["research_state"].iteration, 1)
        self.assertEqual(result["research_state"].review_result["verdict"], "pass")
        self.assertEqual(search.queries[-1], "最新数据")
        evidence_events = [
            event for event in result["events"] if event["type"] == "research_evidence_ready"
        ]
        self.assertEqual(len(evidence_events), 2)
        self.assertTrue(evidence_events[-1]["supplementary"])
        self.assertEqual(evidence_events[-1]["iteration"], 1)


if __name__ == "__main__":
    unittest.main()
