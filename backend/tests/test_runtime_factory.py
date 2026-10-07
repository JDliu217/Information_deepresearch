import os
import unittest
from unittest.mock import patch

from app.core.llm_client import MockLLMClient
from app.core.runtime_factory import create_configured_llm, create_configured_search
from app.core.search_client import MockSearchClient


class RuntimeFactoryTests(unittest.TestCase):
    def test_factory_uses_mock_clients_without_keys(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsInstance(create_configured_llm(), MockLLMClient)
            self.assertIsInstance(create_configured_search(), MockSearchClient)

    def test_factory_builds_real_llm_when_key_exists(self):
        with patch.dict(
            os.environ,
            {"LLM_API_KEY": "test-key", "BOCHA_API_KEY": "test-bocha"},
            clear=True,
        ):
            llm = create_configured_llm()
            self.assertEqual(llm.settings.api_key, "test-key")
            self.assertIsNone(llm.client)

    def test_force_real_requires_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                create_configured_llm(force_real=True)


if __name__ == "__main__":
    unittest.main()
