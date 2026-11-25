"""Recurring lighting and black-nylon schedules.

Revision ID: 0005_recurring_schedules
Revises: 0004_operations
Create Date: 2026-11-24

A schedule is a series of revisions. Each revision stores the times that apply
between its effective dates. The exclusion constraint stops two revisions of
the same vidriera and operation type from covering the same calendar day.

Clock times are civil times. The application interprets them in
America/Argentina/Buenos_Aires when it expands an occurrence. The row does not
store that timezone.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_recurring_schedules"
down_revision: str | None = "0004_operations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recurring_operation_schedules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("series_id", sa.Uuid(), nullable=False),
        sa.Column("vidriera_id", sa.Uuid(), nullable=False),
        sa.Column("operation_type", sa.Text(), nullable=False),
        sa.Column("effective_start", sa.Date(), nullable=False),
        sa.Column("effective_end", sa.Date(), nullable=False),
        sa.Column("weekdays", sa.ARRAY(sa.SmallInteger()), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("generates", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "operation_type IN ('artificial_lighting', 'black_nylon')",
            name="ck_schedules_type",
        ),
        sa.CheckConstraint(
            "effective_end >= effective_start",
            name="ck_schedules_period",
        ),
        sa.CheckConstraint("start_time <> end_time", name="ck_schedules_times"),
        sa.CheckConstraint(
            "status IN ('active', 'paused', 'ended')",
            name="ck_schedules_status",
        ),
        sa.CheckConstraint(
            "cardinality(weekdays) > 0 "
            "AND weekdays <@ ARRAY[1, 2, 3, 4, 5, 6, 7]::smallint[]",
            name="ck_schedules_weekdays",
        ),
        sa.ForeignKeyConstraint(
            ["vidriera_id"],
            ["vidrieras.id"],
            name="fk_schedules_vidriera_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "series_id",
            "effective_start",
            name="uq_schedules_series_start",
        ),
    )
    op.create_index(
        "ix_schedules_vidriera_type",
        "recurring_operation_schedules",
        ["vidriera_id", "operation_type", "effective_start"],
    )
    op.execute(
        """
        ALTER TABLE recurring_operation_schedules
        ADD CONSTRAINT ex_schedules_no_overlap
        EXCLUDE USING gist (
            vidriera_id WITH =,
            operation_type WITH =,
            daterange(effective_start, effective_end, '[]') WITH &&
        )
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE recurring_operation_schedules "
        "DROP CONSTRAINT IF EXISTS ex_schedules_no_overlap"
    )
    op.drop_index(
        "ix_schedules_vidriera_type",
        table_name="recurring_operation_schedules",
    )
    op.drop_table("recurring_operation_schedules")
