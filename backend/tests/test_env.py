import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core import env as env_module


class ProjectEnvTests(unittest.TestCase):
    def test_load_project_env_reads_project_file_without_overriding_system_value(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "TEST_PROJECT_ENV_FILE=from-file\nTEST_PROJECT_ENV_SYSTEM=from-file\n",
                encoding="utf-8",
            )
            with patch.object(env_module, "ENV_FILE", env_file):
                with patch.dict(
                    os.environ,
                    {"TEST_PROJECT_ENV_SYSTEM": "from-system"},
                    clear=True,
                ):
                    env_module.load_project_env()
                    self.assertEqual(os.environ["TEST_PROJECT_ENV_FILE"], "from-file")
                    self.assertEqual(os.environ["TEST_PROJECT_ENV_SYSTEM"], "from-system")


if __name__ == "__main__":
    unittest.main()
