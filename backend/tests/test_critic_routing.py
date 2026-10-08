import unittest

from app.agents.critic import CriticAgent


class CriticRoutingTests(unittest.TestCase):
    def test_missing_source_major_issue_routes_to_research(self):
        route = CriticAgent.route_review(
            {
                "structured_issues": [
                    {
                        "issue_type": "missing_source",
                        "severity": "major",
                        "requires_new_search": True,
                        "search_query": "官方统计数据",
                    }
                ],
                "missing_aspects": [],
                "search_queries": [],
            }
        )

        self.assertEqual(route["action"], "research")
        self.assertEqual(route["search_queries"], ["官方统计数据"])

    def test_logic_issue_routes_to_revision(self):
        route = CriticAgent.route_review(
            {
                "structured_issues": [
                    {
                        "issue_type": "logic_error",
                        "severity": "major",
                        "requires_new_search": False,
                    }
                ],
                "missing_aspects": [],
                "search_queries": [],
            }
        )

        self.assertEqual(route["action"], "revise")
        self.assertFalse(route["should_research"])

    def test_missing_aspect_deduplicates_queries(self):
        route = CriticAgent.route_review(
            {
                "structured_issues": [],
                "missing_aspects": ["区域差异", "区域差异"],
                "search_queries": ["区域差异"],
            }
        )

        self.assertEqual(route["search_queries"], ["区域差异"])
        self.assertEqual(route["action"], "research")

    def test_one_of_four_serious_issues_does_not_cross_research_threshold(self):
        route = CriticAgent.route_review(
            {
                "structured_issues": [
                    {
                        "issue_type": "outdated",
                        "severity": "major",
                        "requires_new_search": True,
                        "search_query": "最新行业数据",
                    },
                    *[
                        {
                            "issue_type": "logic_error",
                            "severity": "major",
                            "requires_new_search": False,
                        }
                        for _ in range(3)
                    ],
                ],
                "missing_aspects": [],
            }
        )

        self.assertEqual(route["action"], "revise")
        self.assertFalse(route["should_research"])

    def test_two_of_five_serious_issues_cross_research_threshold(self):
        route = CriticAgent.route_review(
            {
                "structured_issues": [
                    {
                        "issue_type": "missing_source",
                        "severity": "major",
                        "requires_new_search": True,
                        "search_query": "官方来源",
                    },
                    {
                        "issue_type": "outdated",
                        "severity": "critical",
                        "requires_new_search": True,
                        "search_query": "最新行业数据",
                    },
                    *[
                        {
                            "issue_type": "logic_error",
                            "severity": "major",
                            "requires_new_search": False,
                        }
                        for _ in range(3)
                    ],
                ],
                "missing_aspects": [],
            }
        )

        self.assertEqual(route["action"], "research")
        self.assertEqual(
            set(route["search_queries"]), {"官方来源", "最新行业数据"}
        )


if __name__ == "__main__":
    unittest.main()
