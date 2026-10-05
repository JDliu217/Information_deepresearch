import unittest

from app.domain.state import ResearchState


class ResearchStateTests(unittest.TestCase):
    def test_state_starts_empty(self):
        state = ResearchState("测试问题")

        self.assertEqual(state.query, "测试问题")
        self.assertEqual(state.phase, "init")
        self.assertEqual(state.plan, [])
        self.assertEqual(state.sources, [])
        self.assertEqual(state.facts, [])

    def test_mutable_fields_are_not_shared(self):
        first = ResearchState("第一个问题")
        second = ResearchState("第二个问题")

        first.plan.append({"title": "只属于第一个任务"})

        self.assertEqual(len(first.plan), 1)
        self.assertEqual(second.plan, [])


if __name__ == "__main__":
    unittest.main()
