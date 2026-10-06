import unittest

from app.domain.state import ResearchState


class ResearchStateTests(unittest.TestCase):
    def test_state_starts_empty(self):
        state = ResearchState("测试问题")

        self.assertEqual(state.query, "测试问题")
        self.assertEqual(state.phase, "init")
        self.assertEqual(state.outline, [])
        self.assertEqual(state.hypotheses, [])
        self.assertEqual(state.knowledge_graph, {"nodes": [], "edges": []})
        self.assertEqual(state.raw_sources, [])
        self.assertEqual(state.facts, [])
        self.assertEqual(state.data_points, [])
        self.assertEqual(state.charts, [])
        self.assertEqual(state.messages, [])
        self.assertFalse(hasattr(state, "plan"))
        self.assertFalse(hasattr(state, "sources"))
        self.assertFalse(hasattr(state, "review"))

    def test_mutable_fields_are_not_shared(self):
        first = ResearchState("第一个问题")
        second = ResearchState("第二个问题")

        first.outline.append({"title": "只属于第一个任务"})
        first.hypotheses.append({"id": "h-1"})
        first.knowledge_graph["nodes"].append({"id": "node-1"})
        first.data_points.append({"id": "dp-1"})
        first.charts.append({"id": "chart-1"})
        first.messages.append({"type": "progress"})

        self.assertEqual(len(first.outline), 1)
        self.assertEqual(second.outline, [])
        self.assertEqual(second.hypotheses, [])
        self.assertEqual(second.knowledge_graph, {"nodes": [], "edges": []})
        self.assertEqual(second.data_points, [])
        self.assertEqual(second.charts, [])
        self.assertEqual(second.messages, [])


if __name__ == "__main__":
    unittest.main()
