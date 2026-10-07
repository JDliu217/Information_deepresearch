"""构建 DeepResearch 的 LangGraph 图。"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from .nodes import ResearchGraphNodes
from .routes import select_review_route
from .state import ResearchGraphState


def build_research_graph(nodes: ResearchGraphNodes):
    """构建当前 I7 的线性主图。

    审核节点后的条件边会进入补充研究、直接修订或结束节点，并在研究
    与写作后回到审核节点。
    """

    graph = StateGraph(ResearchGraphState)
    graph.add_node("start", nodes.start)
    graph.add_node("plan", nodes.plan)
    graph.add_node("research", nodes.research)
    graph.add_node("extract_facts", nodes.extract_facts)
    graph.add_node("analyze", nodes.analyze)
    graph.add_node("execute_analysis", nodes.execute_analysis)
    graph.add_node("write", nodes.write)
    graph.add_node("review", nodes.review)
    graph.add_node("route_review", nodes.route_review)
    graph.add_node("complete", nodes.complete)

    graph.set_entry_point("start")
    graph.add_edge("start", "plan")
    graph.add_edge("plan", "research")
    graph.add_edge("research", "extract_facts")
    graph.add_edge("extract_facts", "analyze")
    graph.add_edge("analyze", "execute_analysis")
    graph.add_edge("execute_analysis", "write")
    graph.add_edge("write", "review")
    graph.add_edge("review", "route_review")
    graph.add_conditional_edges(
        "route_review",
        select_review_route,
        {
            "research": "research",
            "revise": "write",
            "stop": "complete",
        },
    )
    graph.add_edge("complete", END)
    return graph.compile()
