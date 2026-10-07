import unittest

from app.domain.models import CriticFeedback, FactCheckResult, ReviewResult


class ReviewModelTests(unittest.TestCase):
    def test_critic_feedback_keeps_structured_routing_fields(self):
        feedback = CriticFeedback(
            id="issue-1",
            target_section="sec-2",
            issue_type="missing_source",
            severity="major",
            description="市场规模缺少权威来源",
            suggestion="补充官方统计数据",
            location="第二章节第三段",
            evidence="报告中的数字无法在引用来源中找到",
            requires_new_search=True,
            search_query="市场规模 官方统计",
        )

        result = feedback.to_dict()

        self.assertEqual(result["location"], "第二章节第三段")
        self.assertTrue(result["requires_new_search"])
        self.assertEqual(result["search_query"], "市场规模 官方统计")

    def test_review_result_serializes_fact_checks_and_summary(self):
        result = ReviewResult(
            verdict="needs_revision",
            quality_score=6.5,
            summary="需要补充数据来源",
            issues=["市场规模缺少来源"],
            structured_issues=[{"id": "issue-1", "severity": "major"}],
            fact_check_results=[
                FactCheckResult(
                    fact_id="fact-1",
                    status="suspicious",
                    reason="来源没有直接支撑该数字",
                ).to_dict()
            ],
            missing_aspects=["区域差异"],
            strengths=["章节结构清晰"],
            needs_more_research=True,
            search_queries=["行业区域差异 数据"],
        )

        serialized = result.to_dict()

        self.assertEqual(serialized["quality_score"], 6.5)
        self.assertEqual(serialized["issues"], ["市场规模缺少来源"])
        self.assertEqual(serialized["structured_issues"][0]["id"], "issue-1")
        self.assertEqual(serialized["fact_check_results"][0]["status"], "suspicious")
        self.assertEqual(serialized["search_queries"], ["行业区域差异 数据"])


if __name__ == "__main__":
    unittest.main()
