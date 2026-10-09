import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


class AlembicMigrationTests(unittest.TestCase):
    def test_upgrade_and_downgrade_work_on_sqlite(self):
        project_root = Path(__file__).resolve().parents[2]
        alembic_config = Config(str(project_root / "alembic.ini"))
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "migration.sqlite"
            alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

            command.upgrade(alembic_config, "001_create_research_tables")
            engine = create_engine(f"sqlite:///{database_path}")
            self.assertEqual(
                set(inspect(engine).get_table_names()),
                {"alembic_version", "research_runs", "research_events"},
            )
            self.assertNotIn(
                "status",
                {column["name"] for column in inspect(engine).get_columns("research_runs")},
            )

            command.upgrade(alembic_config, "head")
            self.assertTrue(
                {"status", "error"}.issubset(
                    {column["name"] for column in inspect(engine).get_columns("research_runs")}
                )
            )

            command.downgrade(alembic_config, "base")
            self.assertEqual(set(inspect(engine).get_table_names()), {"alembic_version"})
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
