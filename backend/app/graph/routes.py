"""LangGraph 的审核后路由。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.agents.critic import CriticAgent

from .state import GraphRoute, ResearchGraphState


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
    needs_research = bool(
        review_route["should_research"] or review.get("needs_more_research")
    )
    if needs_research:
        state.pending_search_queries = (
            review_route["search_queries"]
            or review.get("search_queries", [])
            or review.get("issues", [])
            or state.research_questions
        )
        return {
            "research_state": state,
            "route": "research",
            "supplementary": True,
            "revision": True,
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
