"""构建 DeepResearch 的 LangGraph 图。"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from .nodes import ResearchGraphNodes
from .state import ResearchGraphState


def build_research_graph(nodes: ResearchGraphNodes):
    """构建当前 I7 的线性主图。

    审核后的条件分支会在下一步接入。先把每个节点接通，可以单独验证
    LangGraph 是否正确调用已有 Agent，以及事件 reducer 是否按顺序累积。
    """

    graph = StateGraph(ResearchGraphState)
    graph.add_node("start", nodes.start)
    graph.add_node("plan", nodes.plan)
    graph.add_node("research", nodes.research)
    graph.add_node("write", nodes.write)
    graph.add_node("review", nodes.review)
    graph.add_node("complete", nodes.complete)

    graph.set_entry_point("start")
    graph.add_edge("start", "plan")
    graph.add_edge("plan", "research")
    graph.add_edge("research", "write")
    graph.add_edge("write", "review")
    graph.add_edge("review", "complete")
    graph.add_edge("complete", END)
    return graph.compile()
