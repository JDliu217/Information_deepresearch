"""LangGraph 使用的最小状态适配层。"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict

from app.domain.state import ResearchState


GraphRoute = Literal["pass", "research", "revise", "stop"]


class ResearchGraphState(TypedDict, total=False):
    """图节点之间传递的状态。

    ``research_state`` 是项目唯一的业务状态。``events`` 只是图运行期间
    收集的对外事件，使用 LangGraph reducer 追加，不覆盖前一个节点的事件。
    ``supplementary`` 和 ``revision`` 用来告诉研究和写作节点当前是否处于
    审核后的补充轮次。
    """

    research_state: ResearchState
    events: Annotated[list[dict[str, Any]], operator.add]
    route: GraphRoute
    supplementary: bool
    revision: bool


def initial_graph_state(state: ResearchState) -> ResearchGraphState:
    """把领域状态包装成图的初始输入。"""

    return {
        "research_state": state,
        "events": [],
        "route": "stop",
        "supplementary": False,
        "revision": False,
    }
