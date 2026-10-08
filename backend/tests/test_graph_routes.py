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


def review(
    verdict,
    *,
    more_research=False,
    issues=None,
    structured_issues=None,
    search_queries=None,
    score=5.0,
):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "structured_issues": structured_issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)
        self.critic_calls = 0

    async def complete_json(self, role, payload):
        if role == "critic":
            self.critic_calls += 1
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
            structured_issues=[
                {
                    "target_section": "sec-1",
                    "issue_type": "outdated",
                    "severity": "major",
                    "requires_new_search": True,
                    "search_query": "最新数据",
                }
            ],
        )
        state.outline = [{"id": "sec-1", "title": "章节一", "status": "drafted"}]

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

    def test_minor_issue_does_not_bypass_critic_research_threshold(self):
        state = ResearchState("测试问题", max_iterations=1)
        state.review_result = review(
            "needs_revision",
            more_research=True,
            search_queries=["模型建议的查询"],
            structured_issues=[
                {
                    "issue_type": "logic_error",
                    "severity": "minor",
                    "requires_new_search": False,
                }
            ],
        )

        result = prepare_review_route(initial_graph_state(state))

        self.assertEqual(result["route"], "revise")
        self.assertFalse(result["supplementary"])
        self.assertEqual(result["research_state"].pending_search_queries, [])

    def test_pass_stops_even_with_low_score_or_unresolved_issues(self):
        state = ResearchState("测试问题", max_iterations=2)
        state.review_result = review(
            "pass",
            more_research=True,
            search_queries=["不要执行的查询"],
            score=4.0,
            structured_issues=[
                {
                    "issue_type": "missing_source",
                    "severity": "critical",
                    "requires_new_search": True,
                    "search_query": "不要执行的查询",
                }
            ],
        )

        result = prepare_review_route(initial_graph_state(state))

        self.assertEqual(result["route"], "stop")
        self.assertEqual(result["research_state"].iteration, 0)

    def test_follow_up_queries_are_researched_before_analysis(self):
        state = ResearchState("测试问题", max_iterations=2)
        state.outline = [{"id": "sec-1", "status": "researching"}]
        state.pending_search_queries = ["追溯来源"]

        from app.graph.routes import select_research_batch_route

        self.assertEqual(
            select_research_batch_route(
                {"research_state": state, "supplementary": True}
            ),
            "follow_up",
        )

    def test_critic_supplementary_returns_to_writer_after_recursive_queries(self):
        from app.graph.routes import select_research_batch_route

        state = ResearchState("测试问题", max_iterations=2)
        state.outline = [{"id": "sec-1", "status": "researching"}]
        graph_state = {
            **initial_graph_state(state),
            "critic_supplementary": True,
            "supplementary": True,
            "revision": True,
        }

        self.assertEqual(select_research_batch_route(graph_state), "write")

        # Critic queries use the supplementary prompt even when a previous
        # recursive round left a nonzero depth in graph state.
        state.pending_search_queries = ["追溯来源"]
        graph_state["research_depth"] = 1
        self.assertEqual(select_research_batch_route(graph_state), "search")

    def test_critic_research_round_resets_recursive_search_depth(self):
        state = ResearchState("测试问题", max_iterations=2)
        state.iteration = 0
        state.outline = [{"id": "sec-1", "title": "章节一", "status": "researching"}]
        state.review_result = {
            **review(
                "needs_revision",
                more_research=True,
                structured_issues=[
                    {
                        "target_section": "sec-1",
                        "search_query": "更新数据",
                        "requires_new_search": True,
                        "issue_type": "outdated",
                        "severity": "major",
                    }
                ],
            ),
        }

        result = prepare_review_route({
            **initial_graph_state(state),
            "research_depth": 2,
        })

        self.assertEqual(result["research_depth"], 0)
        self.assertEqual(
            result["research_state"].pending_search_contexts,
            {"更新数据": [{"section_id": "sec-1", "section_title": "章节一"}]},
        )

    def test_graph_loops_through_supplementary_research(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=[
                        {
                            "issue_type": "outdated",
                            "severity": "major",
                            "requires_new_search": True,
                            "search_query": "最新数据",
                            "description": "需要更新数据",
                            "suggestion": "补充最新数据来源",
                        }
                    ],
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
        evidence_events = [
            event for event in result["events"] if event["type"] == "research_evidence_ready"
        ]
        self.assertEqual(len(evidence_events), 2)
        self.assertTrue(evidence_events[-1]["supplementary"])
        self.assertEqual(evidence_events[-1]["iteration"], 1)
        self.assertEqual(
            sum(event["type"] == "analysis_ready" for event in result["events"]),
            1,
        )
        draft_events = [
            event for event in result["events"] if event["type"] == "draft_ready"
        ]
        self.assertTrue(draft_events[-1]["revision"])

    def test_max_iterations_counts_rework_rounds_like_reference_graph(self):
        for max_iterations in (0, 1, 2):
            with self.subTest(max_iterations=max_iterations):
                non_pass_review = review(
                    "needs_revision",
                    structured_issues=[
                        {
                            "issue_type": "logic_error",
                            "severity": "minor",
                            "requires_new_search": False,
                        }
                    ],
                )
                llm = SequencedReviewLLM(
                    [non_pass_review for _ in range(max_iterations + 1)]
                )
                graph = build_research_graph(
                    make_nodes(llm, GraphRecordingSearchClient())
                )

                result = asyncio.run(
                    graph.ainvoke(
                        initial_graph_state(
                            ResearchState("测试问题", max_iterations=max_iterations)
                        )
                    )
                )

                self.assertEqual(llm.critic_calls, max_iterations + 1)
                self.assertEqual(result["research_state"].iteration, max_iterations)


if __name__ == "__main__":
    unittest.main()


