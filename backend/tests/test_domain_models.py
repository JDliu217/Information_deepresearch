import unittest

from app.domain.models import (
    Chart,
    CriticFeedback,
    DataPoint,
    Hypothesis,
    Section,
)


class DomainModelTests(unittest.TestCase):
    def test_section_serializes_nested_sections(self):
        section = Section(
            id="sec-1",
            title="行业概况",
            description="研究行业规模和定义",
            requires_data=True,
            search_queries=["行业规模"],
            subsections=[Section(id="sec-1-1", title="市场定义")],
        )

        result = section.to_dict()

        self.assertEqual(result["id"], "sec-1")
        self.assertTrue(result["requires_data"])
        self.assertEqual(result["subsections"][0]["title"], "市场定义")

    def test_model_collections_are_not_shared(self):
        first = Hypothesis(id="h-1", content="第一个假设")
        second = Hypothesis(id="h-2", content="第二个假设")

        first.evidence_for.append("支持证据")

        self.assertEqual(first.evidence_for, ["支持证据"])
        self.assertEqual(second.evidence_for, [])

    def test_data_point_and_chart_keep_analysis_fields(self):
        data_point = DataPoint(
            id="dp-1",
            name="市场规模",
            value=120.5,
            unit="亿元",
            year=2025,
            source="https://example.com/source",
            confidence=0.9,
        )
        chart = Chart(
            id="chart-1",
            title="市场规模趋势",
            chart_type="line",
            data={"x": [2024, 2025], "y": [100, 120.5]},
            echarts_option={
                "xAxis": {"type": "category"},
                "series": [{"type": "line", "data": [100, 120.5]}],
            },
            section_id="sec-1",
        )

        self.assertEqual(data_point.to_dict()["year"], 2025)
        self.assertEqual(data_point.to_dict()["confidence"], 0.9)
        self.assertEqual(chart.to_dict()["chart_type"], "line")
        self.assertEqual(chart.to_dict()["echarts_option"]["series"][0]["type"], "line")
        self.assertEqual(chart.to_dict()["section_id"], "sec-1")

    def test_critic_feedback_starts_unresolved(self):
        feedback = CriticFeedback(
            id="issue-1",
            target_section="sec-1",
            issue_type="missing_source",
            severity="major",
            description="关键数据缺少来源",
            suggestion="补充官方统计来源",
        )

        self.assertFalse(feedback.resolved)
        self.assertEqual(feedback.to_dict()["severity"], "major")


if __name__ == "__main__":
    unittest.main()
