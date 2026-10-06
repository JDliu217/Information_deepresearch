import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.workflow.research_workflow import ResearchWorkflow


class ResearchWorkflowTests(unittest.TestCase):
    def test_workflow_runs_full_research_chain(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("中国新能源汽车行业的发展趋势是什么？")
        )

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.plan[0]["title"], "现状与定义")
        self.assertEqual(len(state.sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(state.final_report)
        self.assertEqual(state.review["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)

    def test_workflow_preserves_explicit_session_id(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("测试问题", session_id="session-001")
        )

        self.assertEqual(state.session_id, "session-001")


if __name__ == "__main__":
    unittest.main()
