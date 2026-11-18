"""Production hierarchy.

Revision ID: 0001_production_hierarchy
Revises:
Create Date: 2026-11-16

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_production_hierarchy"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "quintas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=12), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_key", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "code ~ '^[A-Z][A-Z0-9]{1,11}$'",
            name="ck_quintas_code",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_quintas_code"),
        sa.UniqueConstraint("name_key", name="uq_quintas_name"),
    )
    op.create_table(
        "vidrieras",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quinta_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_key", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.CheckConstraint("number >= 1", name="ck_vidrieras_number_positive"),
        sa.CheckConstraint(
            "code ~ '^[A-Z][A-Z0-9]{1,11}-V[0-9]+$'"
            " AND substring(code from '-V([0-9]+)$')::integer = number"
            " AND code = split_part(code, '-V', 1) || '-V' || "
            "lpad(number::text, greatest(3, char_length(number::text)), '0')",
            name="ck_vidrieras_code_matches_number",
        ),
        sa.ForeignKeyConstraint(["quinta_id"], ["quintas.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_vidrieras_code"),
        sa.UniqueConstraint(
            "quinta_id",
            "number",
            name="uq_vidrieras_quinta_number",
        ),
        sa.UniqueConstraint(
            "quinta_id",
            "name_key",
            name="uq_vidrieras_quinta_name",
        ),
    )
    op.create_table(
        "canteros",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vidriera_id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("name_key", sa.String(length=200), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "number >= 1 AND number <= 4",
            name="ck_canteros_number",
        ),
        sa.ForeignKeyConstraint(["vidriera_id"], ["vidrieras.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "vidriera_id",
            "number",
            name="uq_canteros_vidriera_number",
        ),
        sa.UniqueConstraint(
            "vidriera_id",
            "name_key",
            name="uq_canteros_vidriera_name",
        ),
    )


def downgrade() -> None:
    op.drop_table("canteros")
    op.drop_table("vidrieras")
    op.drop_table("quintas")
