"""Cultivation cycles for each vidriera.

Revision ID: 0003_cultivation_cycles
Revises: 0002_production_boundaries
Create Date: 2026-11-24

Status is not a column. A cycle is active while end_date is null and finalized
once that date is set, so the two facts cannot disagree.

Overlapping periods of one vidriera are rejected by an exclusion constraint on
an inclusive daterange. An open cycle uses date infinity as its upper bound, so
a later period cannot sit beside an active one. Inclusive bounds treat a cycle
that ends on the day another starts as an overlap. The following day does not.

btree_gist is required because the constraint compares vidriera_id with equality
and a daterange with overlap. Core GiST has no operator class for uuid equality.
The extension is created when missing. Downgrade drops the table and leaves the
extension installed, because removing it would affect the whole database.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_cultivation_cycles"
down_revision: str | None = "0002_production_boundaries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.create_table(
        "cultivation_cycles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vidriera_id", sa.Uuid(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_cultivation_cycles_end_not_before_start",
        ),
        sa.ForeignKeyConstraint(
            ["vidriera_id"],
            ["vidrieras.id"],
            name="fk_cultivation_cycles_vidriera_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_cultivation_cycles_one_active",
        "cultivation_cycles",
        ["vidriera_id"],
        unique=True,
        postgresql_where=sa.text("end_date IS NULL"),
    )
    op.create_index(
        "ix_cultivation_cycles_vidriera_start",
        "cultivation_cycles",
        ["vidriera_id", "start_date"],
    )
    op.execute(
        """
        ALTER TABLE cultivation_cycles
        ADD CONSTRAINT ex_cultivation_cycles_no_overlap
        EXCLUDE USING gist (
            vidriera_id WITH =,
            daterange(
                start_date,
                COALESCE(end_date, 'infinity'::date),
                '[]'
            ) WITH &&
        )
        """
    )


def downgrade() -> None:
    op.drop_table("cultivation_cycles")
