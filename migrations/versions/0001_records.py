"""Create the atlas records persistence baseline.

Revision ID: 0001_records
Revises:
Create Date: 2026-09-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_records"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "atlas_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_atlas_records_kind", "atlas_records", ["kind"], unique=False)
    op.create_index("ix_atlas_records_key", "atlas_records", ["key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_atlas_records_key", table_name="atlas_records")
    op.drop_index("ix_atlas_records_kind", table_name="atlas_records")
    op.drop_table("atlas_records")
