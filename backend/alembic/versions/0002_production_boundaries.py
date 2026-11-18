"""Optional GeoJSON boundaries for quintas and vidrieras.

Revision ID: 0002_production_boundaries
Revises: 0001_production_hierarchy
Create Date: 2026-11-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_production_boundaries"
down_revision: str | None = "0001_production_hierarchy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "quintas",
        sa.Column("boundary", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "vidrieras",
        sa.Column("boundary", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("vidrieras", "boundary")
    op.drop_column("quintas", "boundary")
