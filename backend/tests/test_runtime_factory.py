import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core import env as env_module
from app.core.llm_client import MockLLMClient
from app.core.runtime_factory import (
    create_configured_llm,
    create_configured_runtime,
    create_configured_search,
)
from app.core.search_client import MockSearchClient


class RuntimeFactoryTests(unittest.TestCase):
    def test_factory_uses_mock_clients_without_keys(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(os.environ, {}, clear=True):
                self.assertIsInstance(create_configured_llm(), MockLLMClient)
                self.assertIsInstance(create_configured_search(), MockSearchClient)

    def test_factory_builds_real_llm_when_key_exists(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(
                os.environ,
                {"LLM_API_KEY": "test-key", "BOCHA_API_KEY": "test-bocha"},
                clear=True,
            ):
                llm = create_configured_llm()
                self.assertEqual(llm.settings.api_key, "test-key")
                self.assertIsNone(llm.client)

    def test_force_real_requires_configuration(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    create_configured_llm(force_real=True)

    def test_configured_runtime_defaults_to_three_review_iterations(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(os.environ, {}, clear=True):
                runtime = create_configured_runtime()

        self.assertEqual(runtime.max_iterations, 3)

    def test_configured_runtime_reads_review_iteration_limit_from_environment(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(os.environ, {"RESEARCH_MAX_ITERATIONS": "2"}, clear=True):
                runtime = create_configured_runtime()

        self.assertEqual(runtime.max_iterations, 2)

    def test_configured_runtime_rejects_invalid_review_iteration_limit(self):
        with patch.object(env_module, "ENV_FILE", Path("missing-test.env")):
            with patch.dict(os.environ, {"RESEARCH_MAX_ITERATIONS": "many"}, clear=True):
                with self.assertRaisesRegex(ValueError, "RESEARCH_MAX_ITERATIONS"):
                    create_configured_runtime()


if __name__ == "__main__":
    unittest.main()
