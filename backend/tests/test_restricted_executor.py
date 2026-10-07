import unittest

from app.execution.restricted_executor import RestrictedCodeExecutor


class RestrictedCodeExecutorTests(unittest.TestCase):
    def setUp(self):
        self.executor = RestrictedCodeExecutor()
        self.context = {
            "data_points": [{"value": 10}, {"value": 20}],
            "facts": [],
            "insights": [],
            "charts": [],
        }

    def test_executes_small_statistical_script(self):
        execution = self.executor.execute(
            "result = {'count': len(data_points)}\nprint(result)",
            self.context,
            execution_id="exec-1",
        )

        self.assertEqual(execution.status, "succeeded")
        self.assertEqual(execution.result, {"count": 2})
        self.assertIn("count", execution.stdout)
        self.assertIsNotNone(execution.duration_ms)

    def test_rejects_import_and_attribute_access(self):
        for code in ("import os", "data_points.__class__"):
            with self.subTest(code=code):
                execution = self.executor.execute(code, self.context)
                self.assertEqual(execution.status, "rejected")

    def test_records_runtime_failure(self):
        execution = self.executor.execute("result = 1 / 0", self.context)

        self.assertEqual(execution.status, "failed")
        self.assertIn("division", execution.error)

    def test_rejects_unknown_context_fields(self):
        execution = self.executor.execute(
            "print('ok')",
            {**self.context, "secret": "not allowed"},
        )

        self.assertEqual(execution.status, "rejected")
        self.assertIn("secret", execution.error)

    def test_rejects_loops_dynamic_calls_and_large_code(self):
        for code in (
            "while True: pass",
            "getattr(data_points, 'clear')()",
            "result = 2 ** 1000000",
            "print('x')\n" * 1000,
        ):
            with self.subTest(code=code[:30]):
                execution = self.executor.execute(code, self.context)
                self.assertEqual(execution.status, "rejected")

    def test_rejects_result_larger_than_limit(self):
        execution = self.executor.execute(
            "result = {'items': [data_points, data_points]}",
            {"data_points": ["x" * 60_000]},
        )

        self.assertEqual(execution.status, "rejected")
        self.assertIn("分析结果超过长度限制", execution.error)


if __name__ == "__main__":
    unittest.main()
