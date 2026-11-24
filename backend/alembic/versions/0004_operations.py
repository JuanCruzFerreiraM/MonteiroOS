"""Manual operations for a vidriera.

Revision ID: 0004_operations
Revises: 0003_cultivation_cycles
Create Date: 2026-11-24

An operation belongs to one vidriera. The optional cycle is constrained to that
same vidriera through a composite foreign key. Status of the cycle is not
copied: a finalized cycle remains selectable for backfill.

Future timestamps are rejected in the application, with a five-minute clock
tolerance. A database check against now() would invalidate the row later.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_operations"
down_revision: str | None = "0003_cultivation_cycles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_cultivation_cycles_id_vidriera",
        "cultivation_cycles",
        ["id", "vidriera_id"],
    )
    op.create_table(
        "operations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vidriera_id", sa.Uuid(), nullable=False),
        sa.Column("operation_type", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cycle_id", sa.Uuid(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("interval_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("interval_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timing_basis", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "operation_type IN ("
            "'irrigation', 'artificial_lighting', 'black_nylon', "
            "'cold_protection_heating', 'product_application', "
            "'manual_labor', 'observation')",
            name="ck_operations_type",
        ),
        sa.CheckConstraint("origin = 'manual'", name="ck_operations_origin"),
        sa.CheckConstraint(
            "(interval_start IS NULL AND interval_end IS NULL) "
            "OR (interval_start IS NOT NULL AND interval_end IS NOT NULL "
            "AND interval_end > interval_start)",
            name="ck_operations_interval",
        ),
        sa.CheckConstraint(
            "interval_start IS NULL OR operation_type IN "
            "('artificial_lighting', 'black_nylon')",
            name="ck_operations_interval_type",
        ),
        sa.CheckConstraint(
            "(interval_start IS NULL AND timing_basis IS NULL) "
            "OR (interval_start IS NOT NULL AND timing_basis = 'operator_entered')",
            name="ck_operations_timing_basis",
        ),
        sa.ForeignKeyConstraint(
            ["vidriera_id"],
            ["vidrieras.id"],
            name="fk_operations_vidriera_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cycle_id", "vidriera_id"],
            ["cultivation_cycles.id", "cultivation_cycles.vidriera_id"],
            name="fk_operations_cycle_same_vidriera",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_operations_vidriera_occurred",
        "operations",
        ["vidriera_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_operations_vidriera_occurred", table_name="operations")
    op.drop_table("operations")
    op.drop_constraint(
        "uq_cultivation_cycles_id_vidriera",
        "cultivation_cycles",
        type_="unique",
    )
