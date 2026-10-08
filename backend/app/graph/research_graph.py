"""构建 DeepResearch 的 LangGraph 图。"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from .nodes import ResearchGraphNodes
from .routes import select_research_batch_route, select_review_route
from .state import ResearchGraphState


def build_research_graph(nodes: ResearchGraphNodes, *, checkpointer=None):
    """构建 V2 主图。

    阶段开始事件使用独立节点，这样事件流会在耗时 Agent 运行前发出。
    审核后的条件边进入补充研究、直接修订或结束节点。
    """

    graph = StateGraph(ResearchGraphState)
    graph.add_node("start", nodes.start)
    graph.add_node("planning_started", nodes.planning_started)
    graph.add_node("plan", nodes.plan)
    graph.add_node("research_started", nodes.research_started)
    graph.add_node("research", nodes.research)
    graph.add_node("extract_facts", nodes.extract_facts)
    graph.add_node("prepare_follow_up_research", nodes.prepare_follow_up_research)
    graph.add_node("analysis_started", nodes.analysis_started)
    graph.add_node("analyze", nodes.analyze)
    graph.add_node("execute_analysis", nodes.execute_analysis)
    graph.add_node("writing_started", nodes.writing_started)
    graph.add_node("write", nodes.write)
    graph.add_node("reviewing_started", nodes.reviewing_started)
    graph.add_node("review", nodes.review)
    graph.add_node("route_review", nodes.route_review)
    graph.add_node("complete", nodes.complete)

    graph.set_entry_point("start")
    graph.add_edge("start", "planning_started")
    graph.add_edge("planning_started", "plan")
    graph.add_edge("plan", "research_started")
    graph.add_edge("research_started", "research")
    graph.add_edge("research", "extract_facts")
    graph.add_conditional_edges(
        "extract_facts",
        select_research_batch_route,
        {
            "search": "research_started",
            "follow_up": "prepare_follow_up_research",
            "analyze": "analysis_started",
            "write": "writing_started",
        },
    )
    graph.add_edge("prepare_follow_up_research", "research_started")
    graph.add_edge("analysis_started", "analyze")
    graph.add_edge("analyze", "execute_analysis")
    graph.add_edge("execute_analysis", "writing_started")
    graph.add_edge("writing_started", "write")
    graph.add_edge("write", "reviewing_started")
    graph.add_edge("reviewing_started", "review")
    graph.add_edge("review", "route_review")
    graph.add_conditional_edges(
        "route_review",
        select_review_route,
        {
            "research": "research_started",
            "revise": "writing_started",
            "stop": "complete",
        },
    )
    graph.add_edge("complete", END)
    return graph.compile(checkpointer=checkpointer)
