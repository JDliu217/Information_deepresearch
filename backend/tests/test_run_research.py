import asyncio
import unittest
from contextlib import redirect_stdout
from io import StringIO

from app.scripts.run_research import print_state, run


class RunResearchScriptTests(unittest.TestCase):
    def test_script_run_returns_completed_state(self):
        state = asyncio.run(run("测试行业的现状是什么？"))

        self.assertEqual(state.phase, "completed")
        self.assertTrue(state.final_report)

    def test_print_state_contains_key_sections(self):
        state = asyncio.run(run("测试行业的现状是什么？"))
        output = StringIO()

        with redirect_stdout(output):
            print_state(state)

        text = output.getvalue()
        self.assertIn("研究计划", text)
        self.assertIn("搜索来源", text)
        self.assertIn("结构化事实", text)
        self.assertIn("数据洞察", text)
        self.assertIn("图表配置", text)
        self.assertIn("最终报告", text)
        self.assertIn("审核结果", text)


if __name__ == "__main__":
    unittest.main()
