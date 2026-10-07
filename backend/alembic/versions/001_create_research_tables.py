"""create research run and event tables

Revision ID: 001_create_research_tables
Revises:
Create Date: 2026-10-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "001_create_research_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_DATA = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "research_runs",
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("phase", sa.String(length=40), nullable=False),
        sa.Column("iteration", sa.Integer(), nullable=False),
        sa.Column("max_iterations", sa.Integer(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("review_verdict", sa.String(length=40), nullable=True),
        sa.Column("final_report", sa.Text(), nullable=False),
        sa.Column("state_data", JSON_DATA, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("session_id", name="pk_research_runs"),
    )
    op.create_table(
        "research_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("phase", sa.String(length=40), nullable=False),
        sa.Column("iteration", sa.Integer(), nullable=False),
        sa.Column("data", JSON_DATA, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["research_runs.session_id"],
            name="fk_research_events_session_id_research_runs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_research_events"),
        sa.UniqueConstraint(
            "session_id",
            "sequence",
            name="uq_research_events_session_sequence",
        ),
    )
    op.create_index(
        "ix_research_events_session_id",
        "research_events",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_research_events_session_id", table_name="research_events")
    op.drop_table("research_events")
    op.drop_table("research_runs")
