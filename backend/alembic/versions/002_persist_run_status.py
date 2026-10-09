"""persist run status and error details

Revision ID: 002_persist_run_status
Revises: 001_create_research_tables
Create Date: 2026-10-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_persist_run_status"
down_revision: Union[str, None] = "001_create_research_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "research_runs",
        sa.Column(
            "status",
            sa.String(length=40),
            server_default=sa.text("'running'"),
            nullable=False,
        ),
    )
    op.add_column("research_runs", sa.Column("error", sa.Text(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE research_runs SET status = 'completed' "
            "WHERE phase = 'completed'"
        )
    )


def downgrade() -> None:
    op.drop_column("research_runs", "error")
    op.drop_column("research_runs", "status")
