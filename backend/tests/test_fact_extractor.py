import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenFactClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "extracted_facts": [
                {
                    "content": "这条事实引用了不存在的来源。",
                    "source_url": "https://unknown.example.com",
                    "confidence": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class HypothesisFactClient(LLMClient):
    def __init__(self, support, hypothesis_id="h-1"):
        self.support = support
        self.hypothesis_id = hypothesis_id

    async def complete_json(self, role, payload):
        facts = []
        for source in payload["sources"]:
            facts.append(
                {
                    "content": f"关于假设的证据：{source['title']}",
                    "source_title": source["title"],
                    "source_url": source["url"],
                    "confidence": 0.9,
                    "related_hypothesis": self.hypothesis_id,
                    "hypothesis_support": self.support,
                }
            )
        return {
            "extracted_facts": facts,
            "hypothesis_evidence": [
                {
                    "hypothesis_id": self.hypothesis_id,
                    "evidence_type": self.support,
                    "evidence_summary": f"来自 {source['title']} 的证据",
                }
                for source in payload["sources"]
            ],
        }

    async def complete_text(self, role, payload):
        return ""


class InvalidDataPointFactClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "extracted_facts": [
                {
                    "content": "包含无效数据点的事实。",
                    "source_url": payload["sources"][0]["url"],
                    "confidence": 0.8,
                    "data_points": [{"value": 100}],
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class EntityFactClient(LLMClient):
    def __init__(self, entities):
        self.entities = entities

    async def complete_json(self, role, payload):
        source = payload["sources"][0]
        return {
            "extracted_facts": [
                {
                    "content": "一条用于构建知识图谱的事实。",
                    "source_url": source["url"],
                    "confidence": 0.8,
                }
            ],
            "entities_discovered": self.entities,
        }

    async def complete_text(self, role, payload):
        return ""


class CapturingFactClient(LLMClient):
    def __init__(self):
        self.payload = None

    async def complete_json(self, role, payload):
        self.payload = payload
        source = payload["sources"][0]
        return {
            "extracted_facts": [
                {
                    "content": "压缩正文中的事实。",
                    "source_name": source.get("source", "来源"),
                    "source_url": source["url"],
                    "credibility_score": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class FollowUpFactClient(LLMClient):
    async def complete_json(self, role, payload):
        source = payload["sources"][0]
        return {
            "extracted_facts": [
                {
                    "content": "需要追溯来源的事实。",
                    "source_name": source["source"],
                    "source_url": source["url"],
                    "credibility_score": 0.8,
                }
            ],
            "source_tracing_queries": ["原始统计来源"],
            "follow_up_queries": ["补充年度数据"],
        }

    async def complete_text(self, role, payload):
        return ""


class MixedFactClient(LLMClient):
    async def complete_json(self, role, payload):
        source = payload["sources"][0]
        return {
            "facts": [{"content": "旧字段缺少来源"}],
            "extracted_facts": [
                {
                    "content": "参考字段中的有效事实。",
                    "source_name": source["source"],
                    "source_url": source["url"],
                    "credibility_score": 0.9,
                }
            ],
        }

    async def complete_text(self, role, payload):
        return ""


class RepairingFactClient(LLMClient):
    def __init__(self):
        self.calls = []

    async def complete_json(self, role, payload, system_prompt="", user_prompt=""):
        self.calls.append((payload, system_prompt, user_prompt))
        if len(self.calls) == 1:
            source = payload["sources"][0]
            return {
                "extracted_facts": [
                    {"content": "该条事实缺少来源 URL"},
                    {
                        "content": "同批次中另一条有效事实。",
                        "source_name": source["source"],
                        "source_url": source["url"],
                        "credibility_score": 0.8,
                    },
                ]
            }
        source = payload["sources"][0]
        return {
            "extracted_facts": [
                {
                    "content": "修复后保留有来源的事实。",
                    "source_name": source["source"],
                    "source_url": source["url"],
                    "credibility_score": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
        return ""


class ModeAnalysisFactClient(LLMClient):
    def __init__(self):
        self.calls = []

    async def complete_json(
        self,
        role,
        payload,
        system_prompt="",
        user_prompt="",
        temperature=None,
        max_tokens=None,
    ):
        self.calls.append(
            {
                "role": role,
                "payload": payload,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        source = payload["sources"][0]
        query = payload.get("search_query", payload.get("query", "normal"))
        marker = "1002" if "二" in query or "线索" in query else "1001"
        fact = {
            "content": f"针对 {query} 的第 {marker} 项可引用事实。",
            "source_name": source.get("source", "来源"),
            "source_url": source["url"],
            "credibility_score": 0.8,
            "data_points": [
                {"name": "事实内嵌指标", "value": "5", "unit": "个", "year": 2024}
            ],
        }
        if payload["mode"] == "supplementary_search":
            return {
                "extracted_facts": [fact],
                "key_findings": "补充发现",
                "data_points": [{"name": "不应回写", "value": 99}],
            }
        if payload["mode"] == "deep_search":
            fact.pop("data_points")
            fact["related_hypothesis"] = "h-1"
            fact["hypothesis_support"] = "supports"
            return {
                "extracted_facts": [fact],
                "data_points": [
                    {"name": f"递归指标 {query}", "value": 10, "unit": "项", "year": 2024}
                ],
                "further_tracing_queries": [f"继续追溯 {query}"],
                "source_reliability": "来源可追溯",
            }
        return {"extracted_facts": [fact]}

    async def complete_text(self, role, payload, system_prompt="", user_prompt=""):
        return ""


class FactExtractorAgentTests(unittest.TestCase):
    def test_fact_extractor_analyzes_three_sections_concurrently_in_stable_order(self):
        class ConcurrentClient(LLMClient):
            def __init__(self):
                self.active = 0
                self.max_active = 0

            async def complete_json(
                self,
                role,
                payload,
                system_prompt="",
                user_prompt="",
                temperature=None,
                max_tokens=None,
            ):
                self.active += 1
                self.max_active = max(self.max_active, self.active)
                try:
                    section_id = payload["section"]["id"]
                    await asyncio.sleep((5 - int(section_id[-1])) * 0.01)
                    source = payload["sources"][0]
                    return {
                        "extracted_facts": [
                            {
                                "content": f"来自 {section_id} 的事实",
                                "source_name": source["source"],
                                "source_url": source["url"],
                                "credibility_score": 0.8,
                            }
                        ]
                    }
                finally:
                    self.active -= 1

            async def complete_text(self, role, payload):
                return ""

        async def run():
            client = ConcurrentClient()
            state = ResearchState("测试问题")
            state.outline = [
                {"id": f"sec-{index}", "title": f"章节 {index}"}
                for index in range(1, 5)
            ]
            state.raw_sources = [
                {
                    "title": f"来源 {index}",
                    "url": f"https://example.com/{index}",
                    "source": "测试站点",
                    "summary": "摘要",
                    "section_id": f"sec-{index}",
                }
                for index in range(1, 5)
            ]
            await FactExtractorAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())

        self.assertEqual(client.max_active, 3)
        self.assertEqual(
            [fact["section_id"] for fact in state.facts],
            ["sec-1", "sec-2", "sec-3", "sec-4"],
        )

    def test_fact_extractor_calls_once_per_section_with_reference_limits(self):
        class CapturingClient(LLMClient):
            def __init__(self):
                self.payloads = []

            async def complete_json(self, role, payload):
                self.payloads.append(payload)
                sources = payload["sources"]
                return {
                    "extracted_facts": [
                        {
                            "content": f"事实来自 {sources[0]['title']}",
                            "source_name": sources[0]["source"],
                            "source_url": sources[0]["url"],
                            "credibility_score": 0.8,
                        }
                    ]
                }

            async def complete_text(self, role, payload):
                return ""

        async def run():
            client = CapturingClient()
            state = ResearchState("测试问题")
            state.outline = [
                {"id": "sec-a", "title": "章节 A", "description": "A 描述"},
                {"id": "sec-b", "title": "章节 B", "description": "B 描述"},
            ]
            state.raw_sources = [
                {
                    "title": f"来源 {index}",
                    "url": f"https://example.com/{index}",
                    "source": "测试站点",
                    "date": "2025-01-01",
                    "summary": "摘要内容" * 100,
                    "section_id": "sec-a" if index < 20 else "sec-b",
                    "section_title": "章节 A" if index < 20 else "章节 B",
                }
                for index in range(1, 22)
            ]
            await FactExtractorAgent(client).run(state)
            return state, client

        state, client = asyncio.run(run())

        self.assertEqual(len(client.payloads), 2)
        self.assertEqual([len(item["sources"]) for item in client.payloads], [15, 2])
        self.assertTrue(
            all(len(source["content"]) <= 300 for item in client.payloads for source in item["sources"])
        )
        self.assertEqual([item["section"]["id"] for item in client.payloads], ["sec-a", "sec-b"])
        self.assertEqual(len(state.facts), 2)
        self.assertEqual({fact["section_id"] for fact in state.facts}, {"sec-a", "sec-b"})

    def test_fact_extractor_compacts_large_source_context(self):
        client = CapturingFactClient()
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "长正文",
                "url": "https://example.com/long",
                "content": "前文" * 6_000,
            }
        ]

        asyncio.run(FactExtractorAgent(client).run(state))

        sent_content = client.payload["sources"][0]["content"]
        self.assertLessEqual(len(sent_content), FactExtractorAgent.default_max_source_chars)
        self.assertEqual(len(sent_content), FactExtractorAgent.default_max_source_chars)
        self.assertTrue(sent_content.startswith("前文"))
        self.assertGreater(len(state.raw_sources[0]["content"]), len(sent_content))

    def test_fact_extractor_queues_source_tracing_and_follow_up_queries(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "来源",
                "url": "https://example.com/source",
                "source": "测试站点",
                "summary": "摘要",
            }
        ]

        asyncio.run(FactExtractorAgent(FollowUpFactClient()).run(state))

        self.assertEqual(
            state.pending_search_queries,
            ["原始统计来源", "补充年度数据"],
        )

    def test_fact_extractor_prefers_reference_facts_over_invalid_legacy_field(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "来源",
                "url": "https://example.com/source",
                "source": "测试站点",
                "summary": "摘要",
            }
        ]

        asyncio.run(FactExtractorAgent(MixedFactClient()).run(state))

        self.assertEqual([fact["content"] for fact in state.facts], ["参考字段中的有效事实。"])

    def test_fact_extractor_skips_malformed_fact_and_keeps_valid_sibling(self):
        client = RepairingFactClient()
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "来源",
                "url": "https://example.com/source",
                "source": "测试站点",
                "summary": "摘要",
            }
        ]

        asyncio.run(FactExtractorAgent(client).run(state))

        self.assertEqual(len(client.calls), 1)
        self.assertEqual(len(state.facts), 1)
        self.assertEqual(state.facts[0]["source_url"], "https://example.com/source")
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_fact_extractor_skips_unknown_source_url_without_persisting_it(self):
        class CountingBrokenFactClient(BrokenFactClient):
            def __init__(self):
                self.calls = 0

            async def complete_json(self, role, payload):
                self.calls += 1
                return await super().complete_json(role, payload)

        client = CountingBrokenFactClient()
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/source", "summary": "摘要"}
        ]

        asyncio.run(FactExtractorAgent(client).run(state))

        self.assertEqual(client.calls, 1)
        self.assertEqual(state.facts, [])

    def test_fact_extractor_rejects_null_content_without_logging_values(self):
        warnings = []
        facts = FactExtractorAgent._validate_facts(
            [{"content": None, "source_url": "https://example.com/source"}],
            [{"url": "https://example.com/source"}],
            [],
            warnings,
        )
        self.assertEqual(facts, [])
        self.assertTrue(any("缺少 content 或 source_url" in warning for warning in warnings))

    def test_fact_extractor_turns_raw_sources_into_facts(self):
        class RepeatedEvidenceSearchClient(MockSearchClient):
            async def search(self, query, limit=3):
                results = await super().search(query, limit)
                for result in results:
                    result.snippet = "同一条模拟证据，用于明确验证来源间的事实去重。"
                    result.summary = result.snippet
                return results

        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            # Deliberately repeat the evidence text across different URLs so
            # this test covers Scout-compatible cross-source deduplication.
            await ResearcherAgent(RepeatedEvidenceSearchClient()).run(state)
            await FactExtractorAgent(MockLLMClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.facts), 1)
        self.assertTrue(all(fact["source_url"] for fact in state.facts))
        self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
        self.assertEqual(
            {fact["section_id"] for fact in state.facts},
            {"sec_1"},
        )
        self.assertTrue(all(fact["section_title"] for fact in state.facts))
        self.assertTrue(
            all(fact["related_hypothesis"] == "h_1" for fact in state.facts)
        )
        self.assertTrue(
            all(fact["hypothesis_support"] == "supports" for fact in state.facts)
        )
        self.assertEqual(state.hypotheses[0]["status"], "unverified")
        self.assertEqual(state.hypotheses[0]["evidence_for"], [])
        self.assertEqual(len(state.data_points), 1)
        self.assertEqual(
            {point["name"] for point in state.data_points},
            {"模拟来源指标"},
        )
        self.assertTrue(all(point["id"].startswith("dp_") for point in state.data_points))
        self.assertEqual(
            {node["name"] for node in state.knowledge_graph["nodes"]},
            {
                "中国新能源汽车行业的发展趋势是什么？",
                "政策环境",
                "市场需求",
            },
        )
        self.assertEqual(len(state.knowledge_graph["nodes"]), 3)
        self.assertEqual(len(state.knowledge_graph["edges"]), 2)
        self.assertTrue(
            all(
                edge["source"] == "中国新能源汽车行业的发展趋势是什么？"
                for edge in state.knowledge_graph["edges"]
            )
        )

    def test_fact_extractor_builds_and_deduplicates_knowledge_graph(self):
        async def run():
            state = ResearchState("测试问题")
            state.raw_sources = [
                {
                    "title": "来源",
                    "url": "https://example.com/1",
                    "snippet": "证据",
                }
            ]
            entities = [
                {"name": "实体 A", "relations": ["关联实体 B"]},
                {
                    "name": "实体 A",
                    "relations": ["关联实体 B", "关联实体 C"],
                },
                {"name": "实体 B", "type": "policy", "relations": []},
            ]
            agent = FactExtractorAgent(EntityFactClient(entities))
            await agent.run(state)
            await agent.run(state)
            return state

        state = asyncio.run(run())

        self.assertEqual(
            {node["name"] for node in state.knowledge_graph["nodes"]},
            {"实体 A", "实体 B"},
        )
        self.assertEqual(
            {node["id"] for node in state.knowledge_graph["nodes"]},
            {"node_0", "node_1"},
        )
        entity_a = next(
            node
            for node in state.knowledge_graph["nodes"]
            if node["name"] == "实体 A"
        )
        self.assertEqual(entity_a["type"], "unknown")
        self.assertEqual(len(state.knowledge_graph["edges"]), 1)
        self.assertEqual(
            {
                (edge["source"], edge["relation"])
                for edge in state.knowledge_graph["edges"]
            },
            {
                ("实体 A", "关联实体 B"),
            },
        )

    def test_fact_extractor_ignores_invalid_entities_and_keeps_facts(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]

        entities = [
            "实体名不能由 Agent 猜测",
            {"name": "有效实体", "relations": ["有效关系", None]},
            {"name": "", "relations": []},
            {"name": None, "relations": []},
            {"name": "关系字段异常", "relations": "不是列表"},
        ]
        asyncio.run(FactExtractorAgent(EntityFactClient(entities)).run(state))

        self.assertEqual(len(state.facts), 1)
        self.assertEqual(
            [node["name"] for node in state.knowledge_graph["nodes"]],
            ["有效实体", "关系字段异常"],
        )
        self.assertEqual(
            [(edge["source"], edge["relation"]) for edge in state.knowledge_graph["edges"]],
            [("有效实体", "有效关系")],
        )
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_fact_extractor_ignores_non_list_entities(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]

        asyncio.run(FactExtractorAgent(EntityFactClient("不是列表")).run(state))

        self.assertEqual(len(state.facts), 1)
        self.assertEqual(state.knowledge_graph["nodes"], [])
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_fact_extractor_rejects_unknown_source_url(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "已知来源",
                "url": "https://known.example.com",
                "snippet": "摘要",
            }
        ]

        asyncio.run(FactExtractorAgent(BrokenFactClient()).run(state))
        self.assertEqual(state.facts, [])
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_fact_extractor_maps_common_source_url_formatting_to_original(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "已知来源",
                "url": "https://Example.com/source",
                "snippet": "摘要",
            }
        ]

        class FormattingVariantClient(BrokenFactClient):
            async def complete_json(self, role, payload):
                return {
                    "extracted_facts": [
                        {
                            "content": "来源支持的事实",
                            "source_url": " https://example.com/source/ ",
                        }
                    ]
                }

        asyncio.run(FactExtractorAgent(FormattingVariantClient()).run(state))

        self.assertEqual(len(state.facts), 1)
        self.assertEqual(state.facts[0]["source_url"], "https://Example.com/source")

    def test_fact_extractor_requires_sources(self):
        with self.assertRaisesRegex(ValueError, "来源"):
            asyncio.run(FactExtractorAgent(MockLLMClient()).run(ResearchState("测试问题")))

    def test_fact_extractor_marks_hypothesis_as_refuted(self):
        async def run():
            state = ResearchState("测试问题")
            state.raw_sources = [
                {"title": "来源一", "url": "https://example.com/1", "snippet": "证据一"},
                {"title": "来源二", "url": "https://example.com/2", "snippet": "证据二"},
            ]
            state.hypotheses = [
                {
                    "id": "h-1",
                    "content": "待验证假设",
                    "status": "unverified",
                    "evidence_for": [],
                    "evidence_against": [],
                }
            ]
            return await FactExtractorAgent(
                HypothesisFactClient("refutes")
            ).run(state)

        state = asyncio.run(run())

        self.assertEqual(state.hypotheses[0]["status"], "refuted")
        self.assertEqual(len(state.hypotheses[0]["evidence_against"]), 2)

    def test_fact_extractor_keeps_fact_when_hypothesis_is_unknown(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]
        state.hypotheses = [
            {
                "id": "h-1",
                "content": "待验证假设",
                "status": "unverified",
                "evidence_for": [],
                "evidence_against": [],
            }
        ]

        asyncio.run(
            FactExtractorAgent(
                HypothesisFactClient("supports", hypothesis_id="missing")
            ).run(state)
        )

        self.assertEqual(len(state.facts), 1)
        self.assertNotIn("related_hypothesis", state.facts[0])
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_fact_extractor_keeps_fact_when_hypothesis_support_is_invalid(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]
        state.hypotheses = [
            {
                "id": "h-1",
                "content": "待验证假设",
                "status": "unverified",
                "evidence_for": [],
                "evidence_against": [],
            }
        ]

        asyncio.run(FactExtractorAgent(HypothesisFactClient("unsupported")).run(state))

        self.assertEqual(len(state.facts), 1)
        self.assertNotIn("hypothesis_support", state.facts[0])
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_fact_extractor_keeps_only_valid_structured_hypothesis_evidence(self):
        warnings = []

        evidence = FactExtractorAgent._validate_hypothesis_evidence(
            [
                {
                    "hypothesis_id": "h-1",
                    "evidence_type": "支持",
                    "evidence_summary": "有来源支持",
                },
                {
                    "hypothesis_id": "h-1",
                    "evidence_type": "unclear",
                    "evidence_summary": "方向不明",
                },
            ],
            [{"id": "h-1"}],
            warnings,
        )

        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["evidence_type"], "supports")
        self.assertEqual(len(warnings), 1)

    def test_neutral_fact_does_not_change_hypothesis_status(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]
        state.hypotheses = [
            {
                "id": "h-1",
                "content": "待验证假设",
                "status": "unverified",
                "evidence_for": [],
                "evidence_against": [],
            }
        ]

        asyncio.run(FactExtractorAgent(HypothesisFactClient("neutral")).run(state))

        self.assertEqual(state.hypotheses[0]["status"], "partially_supported")

    def test_fact_extractor_skips_invalid_data_point_but_keeps_fact(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]

        asyncio.run(FactExtractorAgent(InvalidDataPointFactClient()).run(state))
        self.assertEqual(len(state.facts), 1)
        self.assertEqual(state.facts[0]["data_points"], [])
        self.assertEqual(state.data_points, [])
        self.assertTrue(
            any(log.get("warning") == "ignored_invalid_optional_fields" for log in state.logs)
        )

    def test_supplementary_mode_uses_reference_prompt_per_query_and_only_adds_facts(self):
        client = ModeAnalysisFactClient()
        state = ResearchState("原始研究问题")
        state.raw_sources = [
            {
                "title": "旧普通来源",
                "url": "https://example.com/old",
                "summary": "旧摘要",
                "query": "旧普通查询",
                "section_id": "sec-1",
                "analysis_mode": "normal",
            }
        ]
        for query in ("补充查询一", "补充查询二"):
            for index in range(9):
                state.raw_sources.append(
                    {
                        "title": f"{query} 来源 {index}",
                        "url": f"https://example.com/{query}/{index}",
                        "source": "测试站点",
                        "summary": "S" * 400,
                        "query": query,
                        "section_id": "sec-1",
                        "section_title": "研究章节",
                        "search_type": "follow_up",
                        "analysis_mode": "supplementary",
                    }
                )

        asyncio.run(FactExtractorAgent(client).run(state, mode="supplementary"))

        self.assertEqual(len(client.calls), 2)
        self.assertEqual(
            [call["payload"]["search_query"] for call in client.calls],
            ["补充查询一", "补充查询二"],
        )
        self.assertTrue(all(len(call["payload"]["sources"]) == 8 for call in client.calls))
        self.assertTrue(
            all(call["system_prompt"] == FactExtractorAgent.SUPPLEMENTARY_ANALYSIS_SYSTEM for call in client.calls)
        )
        self.assertTrue(all(call["temperature"] == 0.2 for call in client.calls))
        first_prompt = client.calls[0]["user_prompt"]
        self.assertIn("原始研究问题", first_prompt)
        self.assertIn("补充查询一", first_prompt)
        self.assertIn("补充查询一 来源 7", first_prompt)
        self.assertNotIn("补充查询一 来源 8", first_prompt)
        self.assertNotIn("S" * 301, first_prompt)
        self.assertEqual(len(state.facts), 2)
        self.assertTrue(all("data_points" not in fact for fact in state.facts))
        self.assertTrue(all(fact["related_sections"] == [] for fact in state.facts))
        self.assertEqual(state.data_points, [])
        self.assertNotIn("旧普通来源", " ".join(call["user_prompt"] for call in client.calls))

    def test_recursive_mode_uses_reference_prompt_and_maps_recursive_outputs(self):
        client = ModeAnalysisFactClient()
        state = ResearchState("原始研究问题")
        state.hypotheses = [
            {
                "id": f"h-{index}",
                "content": f"假设 {index}",
                "status": "unverified",
                "evidence_for": [],
                "evidence_against": [],
            }
            for index in range(1, 5)
        ]
        for query, search_type in (
            ("追溯查询", "source_tracing"),
            ("线索查询", "follow_up"),
        ):
            for index in range(7):
                state.raw_sources.append(
                    {
                        "title": f"{query} 来源 {index}",
                        "url": f"https://example.com/{query}/{index}",
                        "source": "测试站点",
                        "summary": "R" * 400,
                        "query": query,
                        "section_id": "sec-1",
                        "section_title": "研究章节",
                        "search_type": search_type,
                        "analysis_mode": "recursive",
                    }
                )

        asyncio.run(FactExtractorAgent(client).run(state, mode="recursive"))

        self.assertEqual(len(client.calls), 2)
        self.assertEqual(
            [call["payload"]["search_query"] for call in client.calls],
            ["追溯查询", "线索查询"],
        )
        self.assertTrue(all(len(call["payload"]["sources"]) == 6 for call in client.calls))
        self.assertTrue(
            all(call["system_prompt"] == FactExtractorAgent.DEEP_SEARCH_ANALYSIS_SYSTEM for call in client.calls)
        )
        self.assertTrue(all(call["temperature"] == 0.2 for call in client.calls))
        tracing_prompt, follow_up_prompt = [call["user_prompt"] for call in client.calls]
        self.assertIn("追溯原始数据源", tracing_prompt)
        self.assertIn("追踪相关线索", follow_up_prompt)
        self.assertIn("假设 3", tracing_prompt)
        self.assertNotIn("假设 4", tracing_prompt)
        self.assertIn("追溯查询 来源 5", tracing_prompt)
        self.assertNotIn("追溯查询 来源 6", tracing_prompt)
        self.assertNotIn("R" * 301, tracing_prompt)

        self.assertEqual(len(state.facts), 2)
        self.assertEqual(len(state.data_points), 2)
        self.assertEqual(state.hypotheses[0]["status"], "supported")
        self.assertEqual(len(state.hypotheses[0]["evidence_for"]), 2)
        self.assertEqual(
            state.pending_search_queries,
            ["继续追溯 追溯查询", "继续追溯 线索查询"],
        )
        self.assertEqual(
            [
                state.pending_search_contexts[query][0]["search_type"]
                for query in state.pending_search_queries
            ],
            ["source_tracing", "follow_up"],
        )


if __name__ == "__main__":
    unittest.main()
