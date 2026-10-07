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
            "facts": [
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
        return {"facts": facts}

    async def complete_text(self, role, payload):
        return ""


class InvalidDataPointFactClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "facts": [
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
            "facts": [
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
            "facts": [
                {
                    "content": "压缩正文中的事实。",
                    "source_url": source["url"],
                    "confidence": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class FactExtractorAgentTests(unittest.TestCase):
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
        self.assertIn("正文已截断", sent_content)
        self.assertGreater(len(state.raw_sources[0]["content"]), len(sent_content))

    def test_fact_extractor_turns_raw_sources_into_facts(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(MockLLMClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(all(fact["source_url"] for fact in state.facts))
        self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
        self.assertEqual(
            {fact["section_id"] for fact in state.facts},
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertTrue(all(fact["section_title"] for fact in state.facts))
        self.assertTrue(
            all(fact["related_hypothesis"] == "h_1" for fact in state.facts)
        )
        self.assertTrue(
            all(fact["hypothesis_support"] == "supports" for fact in state.facts)
        )
        self.assertEqual(state.hypotheses[0]["status"], "supported")
        self.assertEqual(len(state.hypotheses[0]["evidence_for"]), 3)
        self.assertEqual(len(state.data_points), 3)
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
            {"node_1", "node_2"},
        )
        entity_a = next(
            node
            for node in state.knowledge_graph["nodes"]
            if node["name"] == "实体 A"
        )
        self.assertEqual(entity_a["type"], "unknown")
        self.assertEqual(len(state.knowledge_graph["edges"]), 2)
        self.assertEqual(
            {
                (edge["source"], edge["relation"])
                for edge in state.knowledge_graph["edges"]
            },
            {
                ("实体 A", "关联实体 B"),
                ("实体 A", "关联实体 C"),
            },
        )

    def test_fact_extractor_rejects_invalid_entity_relations(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]

        with self.assertRaisesRegex(ValueError, "relations 必须是列表"):
            asyncio.run(
                FactExtractorAgent(
                    EntityFactClient(
                        [{"name": "实体", "relations": "不是列表"}]
                    )
                ).run(state)
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

        with self.assertRaisesRegex(ValueError, "未知来源"):
            asyncio.run(FactExtractorAgent(BrokenFactClient()).run(state))

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

    def test_fact_extractor_rejects_unknown_hypothesis(self):
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

        with self.assertRaisesRegex(ValueError, "未知假设"):
            asyncio.run(
                FactExtractorAgent(
                    HypothesisFactClient("supports", hypothesis_id="missing")
                ).run(state)
            )

    def test_fact_extractor_rejects_invalid_data_point(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
        ]

        with self.assertRaisesRegex(ValueError, "数据点缺少 name 或 value"):
            asyncio.run(FactExtractorAgent(InvalidDataPointFactClient()).run(state))


if __name__ == "__main__":
    unittest.main()
