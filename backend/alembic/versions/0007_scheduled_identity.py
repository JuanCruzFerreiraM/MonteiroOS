"""Keep a scheduled operation aligned with its confirmation.

Revision ID: 0007_scheduled_identity
Revises: 0006_occurrence_resolutions
Create Date: 2026-11-24

A confirmed scheduled operation keeps the type of the schedule revision.
The resolution carries that same type, and the operation points at the
resolution with both columns. A manual operation has no resolution, so the
composite foreign key does not apply to it.

The occurrence time of a scheduled operation is the actual interval start.
Expected timestamps stay on the resolution and are not part of this check.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0007_scheduled_identity"
down_revision: str | None = "0006_occurrence_resolutions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_schedules_id_type",
        "recurring_operation_schedules",
        ["id", "operation_type"],
    )
    op.create_unique_constraint(
        "uq_resolutions_id_type",
        "occurrence_resolutions",
        ["id", "operation_type"],
    )
    op.create_foreign_key(
        "fk_resolutions_revision_type",
        "occurrence_resolutions",
        "recurring_operation_schedules",
        ["revision_id", "operation_type"],
        ["id", "operation_type"],
    )
    op.create_foreign_key(
        "fk_operations_resolution_type",
        "operations",
        "occurrence_resolutions",
        ["resolution_id", "operation_type"],
        ["id", "operation_type"],
    )
    op.create_check_constraint(
        "ck_operations_scheduled_moment",
        "operations",
        "origin <> 'scheduled' OR occurred_at = interval_start",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_operations_scheduled_moment",
        "operations",
        type_="check",
    )
    op.drop_constraint(
        "fk_operations_resolution_type",
        "operations",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_resolutions_revision_type",
        "occurrence_resolutions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_resolutions_id_type",
        "occurrence_resolutions",
        type_="unique",
    )
    op.drop_constraint(
        "uq_schedules_id_type",
        "recurring_operation_schedules",
        type_="unique",
    )
