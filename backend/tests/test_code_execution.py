import unittest

from app.domain.models import CodeExecution


class CodeExecutionTests(unittest.TestCase):
    def test_execution_record_keeps_analysis_output(self):
        execution = CodeExecution(
            id="exec-1",
            code="print('ok')",
            status="succeeded",
            stdout="ok\n",
            duration_ms=12,
            result={"rows": 2},
            chart_ids=["chart-1"],
        )

        self.assertEqual(
            execution.to_dict(),
            {
                "id": "exec-1",
                "code": "print('ok')",
                "status": "succeeded",
                "stdout": "ok\n",
                "stderr": "",
                "error": "",
                "duration_ms": 12,
                "result": {"rows": 2},
                "chart_ids": ["chart-1"],
            },
        )

    def test_mutable_fields_are_not_shared(self):
        first = CodeExecution(id="exec-1", code="")
        second = CodeExecution(id="exec-2", code="")

        first.chart_ids.append("chart-1")
        first.result["value"] = 1

        self.assertEqual(second.chart_ids, [])
        self.assertEqual(second.result, {})


if __name__ == "__main__":
    unittest.main()
