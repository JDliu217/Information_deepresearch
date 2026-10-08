"""LangGraph 的审核后路由。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.agents.critic import CriticAgent

from .state import GraphRoute, ResearchGraphState


MAX_RESEARCH_FOLLOW_UP_DEPTH = 2


def select_research_batch_route(graph_state: ResearchGraphState) -> str:
    """Continue initial search until every planned section has been researched."""

    state = graph_state["research_state"]
    # FactExtractor queues source-tracing and follow-up queries. Execute those
    # recursive searches before moving to another outline batch, matching the
    # reference DeepScout flow where each section is deepened immediately.
    follow_up_depth = int(graph_state.get("research_depth", 0))
    if (
        state.pending_search_queries
        and state.iteration < state.max_iterations
        and follow_up_depth < MAX_RESEARCH_FOLLOW_UP_DEPTH
    ):
        return "follow_up"
    if any(section.get("status", "pending") == "pending" for section in state.outline):
        return "search"
    return "analyze"


def prepare_review_route(graph_state: ResearchGraphState) -> dict[str, Any]:
    """把 Critic 结果转换成下一张图边。

    通过就结束，达到最大迭代次数也结束；否则根据结构化审核结果决定
    补充搜索或直接修订。
    """

    state = deepcopy(graph_state["research_state"])
    review = state.review_result
    if review.get("verdict") == "pass" or state.iteration >= state.max_iterations:
        return {
            "research_state": state,
            "route": "stop",
            "supplementary": False,
            "revision": False,
        }

    state.iteration += 1
    review_route = CriticAgent.route_review(review)
    # CriticAgent.route_review mirrors the reference CriticMaster's issue-type
    # and severity-ratio rule. The model's `needs_more_research` flag is kept
    # as review metadata, but must not bypass that routing decision.
    needs_research = review_route["should_research"]
    if needs_research:
        state.pending_search_queries = review_route["search_queries"]
        state.pending_search_contexts = _review_search_contexts(
            state.pending_search_queries,
            review.get("structured_issues", []),
            state.outline,
        )
        return {
            "research_state": state,
            "route": "research",
            "supplementary": True,
            "revision": True,
            # A Critic initiated research round is independent of the
            # FactExtractor recursion budget.
            "research_depth": 0,
        }

    return {
        "research_state": state,
        "route": "revise",
        "supplementary": False,
        "revision": True,
    }


def select_review_route(graph_state: ResearchGraphState) -> GraphRoute:
    """返回 LangGraph 条件边使用的路由名称。"""

    return graph_state.get("route", "stop")


def _review_search_contexts(
    queries: list[str], issues: Any, outline: list[dict[str, Any]]
) -> dict[str, list[dict[str, str]]]:
    """Carry each Critic search query back to its cited outline section."""

    contexts: dict[str, list[dict[str, str]]] = {}
    issue_by_query: dict[str, list[dict[str, Any]]] = {}
    if isinstance(issues, list):
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            query = str(issue.get("search_query", "")).strip()
            if query:
                issue_by_query.setdefault(query, []).append(issue)

    section_by_id = {
        str(section.get("id", "")).strip(): section
        for section in outline
        if str(section.get("id", "")).strip()
    }
    for query in queries:
        query = str(query).strip()
        if not query:
            continue
        query_contexts = contexts.setdefault(query, [])
        for issue in issue_by_query.get(query, []):
            section_id = str(issue.get("target_section", "")).strip()
            section = section_by_id.get(section_id)
            if section:
                context = {
                    "section_id": section_id,
                    "section_title": str(section.get("title", "")).strip(),
                }
                if context not in query_contexts:
                    query_contexts.append(context)
    return contexts

