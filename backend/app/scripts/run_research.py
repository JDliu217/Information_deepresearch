"""从命令行运行一次 Mock DeepResearch。"""

from __future__ import annotations

import argparse
import asyncio

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.graph.runtime import create_research_runtime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行一次学习版 DeepResearch")
    parser.add_argument(
        "query",
        nargs="?",
        help="研究问题；不传时会进入交互式输入",
    )
    return parser


def print_state(state: ResearchState) -> None:
    print("\n" + "=" * 60)
    print("研究计划")
    print("=" * 60)
    for index, item in enumerate(state.outline, start=1):
        print(f"{index}. {item['title']}：{item['description']}")

    print("\n" + "=" * 60)
    print(f"搜索来源（{len(state.raw_sources)} 条）")
    print("=" * 60)
    for index, source in enumerate(state.raw_sources, start=1):
        print(f"{index}. {source['title']}")
        print(f"   URL: {source['url']}")

    print("\n" + "=" * 60)
    print(f"结构化事实（{len(state.facts)} 条）")
    print("=" * 60)
    for index, fact in enumerate(state.facts, start=1):
        print(f"{index}. {fact['content']}")
        print(f"   来源: {fact['source_url']}")

    print("\n" + "=" * 60)
    print(f"数据洞察（{len(state.insights)} 条）")
    print("=" * 60)
    for index, insight in enumerate(state.insights, start=1):
        print(f"{index}. {insight}")

    print("\n" + "=" * 60)
    print(f"图表配置（{len(state.charts)} 个）")
    print("=" * 60)
    for index, chart in enumerate(state.charts, start=1):
        print(f"{index}. {chart['title']}（{chart['chart_type']}）")

    print("\n" + "=" * 60)
    print("最终报告")
    print("=" * 60)
    print(state.final_report)

    print("\n" + "=" * 60)
    print("审核结果")
    print("=" * 60)
    print(f"结论: {state.review_result['verdict']}")
    print(f"评分: {state.quality_score}/10")
    print(f"摘要: {state.review_result['summary']}")
    print(f"任务阶段: {state.phase}")
    print(f"会话 ID: {state.session_id}")


async def run(query: str) -> ResearchState:
    runtime = create_research_runtime(MockLLMClient(), MockSearchClient())
    return await runtime.run(query)


def main() -> None:
    args = build_parser().parse_args()
    query = (args.query or input("请输入研究问题：")).strip()
    if not query:
        raise SystemExit("研究问题不能为空")
    state = asyncio.run(run(query))
    print_state(state)


if __name__ == "__main__":
    main()
