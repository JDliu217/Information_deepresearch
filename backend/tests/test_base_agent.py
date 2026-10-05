import asyncio
import unittest

from app.agents.base import BaseAgent
from app.domain.state import ResearchState


class DemoAgent(BaseAgent):
    name = "demo"

    async def run(self, state: ResearchState) -> ResearchState:
        state.phase = "demo_completed"
        return state


class BaseAgentTests(unittest.TestCase):
    def test_concrete_agent_updates_and_returns_state(self):
        state = ResearchState("测试问题")
        agent = DemoAgent()

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "demo_completed")
        self.assertEqual(agent.name, "demo")

    def test_base_agent_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            BaseAgent()


if __name__ == "__main__":
    unittest.main()
