"""Explicit confirmation of scheduled occurrences.

Revision ID: 0006_occurrence_resolutions
Revises: 0005_recurring_schedules
Create Date: 2026-11-24

A resolution stores one human decision for a schedule series and calendar day.
Confirming it also inserts an operation. Marking it as not occurred does not.
Expected timestamps are copied once and are not rewritten when the schedule or
the actual interval changes.

The batch API keeps one transaction and a savepoint per item. That policy
lives in the application. This migration only prevents two resolutions for the
same occurrence.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_occurrence_resolutions"
down_revision: str | None = "0005_recurring_schedules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMING = (
    "("
    "origin = 'manual' AND resolution_id IS NULL AND ("
    "(interval_start IS NULL AND timing_basis IS NULL) OR "
    "(interval_start IS NOT NULL AND timing_basis = 'operator_entered')"
    ")"
    ") OR ("
    "origin = 'scheduled' AND resolution_id IS NOT NULL AND "
    "interval_start IS NOT NULL AND timing_basis IN "
    "('operator_entered', 'assumed_from_schedule')"
    ")"
)


def upgrade() -> None:
    op.create_table(
        "occurrence_resolutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("series_id", sa.Uuid(), nullable=False),
        sa.Column("occurrence_date", sa.Date(), nullable=False),
        sa.Column("revision_id", sa.Uuid(), nullable=False),
        sa.Column("vidriera_id", sa.Uuid(), nullable=False),
        sa.Column("operation_type", sa.Text(), nullable=False),
        sa.Column("expected_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expected_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("confirmation_method", sa.Text(), nullable=False),
        sa.Column("timing_basis", sa.Text(), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cycle_id", sa.Uuid(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "outcome IN ('confirmed', 'not_occurred')",
            name="ck_resolutions_outcome",
        ),
        sa.CheckConstraint(
            "confirmation_method = 'manual'",
            name="ck_resolutions_method",
        ),
        sa.CheckConstraint(
            "expected_end > expected_start",
            name="ck_resolutions_expected",
        ),
        sa.CheckConstraint(
            "operation_type IN ('artificial_lighting', 'black_nylon')",
            name="ck_resolutions_type",
        ),
        sa.CheckConstraint(
            "("
            "outcome = 'confirmed' AND actual_start IS NOT NULL "
            "AND actual_end IS NOT NULL AND actual_end > actual_start "
            "AND timing_basis IN "
            "('assumed_from_schedule', 'operator_entered')"
            ") OR ("
            "outcome = 'not_occurred' AND actual_start IS NULL "
            "AND actual_end IS NULL AND timing_basis IS NULL"
            ")",
            name="ck_resolutions_actual",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"],
            ["recurring_operation_schedules.id"],
            name="fk_resolutions_revision_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vidriera_id"],
            ["vidrieras.id"],
            name="fk_resolutions_vidriera_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cycle_id", "vidriera_id"],
            ["cultivation_cycles.id", "cultivation_cycles.vidriera_id"],
            name="fk_resolutions_cycle_same_vidriera",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "series_id",
            "occurrence_date",
            name="uq_resolutions_series_date",
        ),
    )
    op.create_index(
        "ix_resolutions_vidriera_date",
        "occurrence_resolutions",
        ["vidriera_id", "occurrence_date"],
    )
    op.add_column(
        "operations",
        sa.Column("resolution_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_operations_resolution_id",
        "operations",
        "occurrence_resolutions",
        ["resolution_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_operations_resolution_id",
        "operations",
        ["resolution_id"],
    )
    op.drop_constraint("ck_operations_origin", "operations", type_="check")
    op.drop_constraint("ck_operations_timing_basis", "operations", type_="check")
    op.create_check_constraint(
        "ck_operations_origin",
        "operations",
        "origin IN ('manual', 'scheduled')",
    )
    op.create_check_constraint(
        "ck_operations_timing_basis",
        "operations",
        _TIMING,
    )


def downgrade() -> None:
    op.execute("DELETE FROM operations WHERE origin = 'scheduled'")
    op.drop_constraint("ck_operations_timing_basis", "operations", type_="check")
    op.drop_constraint("ck_operations_origin", "operations", type_="check")
    op.create_check_constraint(
        "ck_operations_origin",
        "operations",
        "origin = 'manual'",
    )
    op.create_check_constraint(
        "ck_operations_timing_basis",
        "operations",
        "(interval_start IS NULL AND timing_basis IS NULL) "
        "OR (interval_start IS NOT NULL AND timing_basis = 'operator_entered')",
    )
    op.drop_constraint("uq_operations_resolution_id", "operations", type_="unique")
    op.drop_constraint(
        "fk_operations_resolution_id",
        "operations",
        type_="foreignkey",
    )
    op.drop_column("operations", "resolution_id")
    op.drop_index("ix_resolutions_vidriera_date", table_name="occurrence_resolutions")
    op.drop_table("occurrence_resolutions")
