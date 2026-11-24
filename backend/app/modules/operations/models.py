import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

_TYPES = (
    "'irrigation', 'artificial_lighting', 'black_nylon', "
    "'cold_protection_heating', 'product_application', "
    "'manual_labor', 'observation'"
)


class Operation(Base):
    """One agricultural activity recorded for a single vidriera.

    ``origin`` distinguishes a manual entry from an operation created by
    confirming a scheduled occurrence. A scheduled confirmation is still this
    same record, not a second table of completed work.
    """

    __tablename__ = "operations"
    __table_args__ = (
        CheckConstraint(
            f"operation_type IN ({_TYPES})",
            name="ck_operations_type",
        ),
        CheckConstraint("origin = 'manual'", name="ck_operations_origin"),
        CheckConstraint(
            "(interval_start IS NULL AND interval_end IS NULL) "
            "OR (interval_start IS NOT NULL AND interval_end IS NOT NULL "
            "AND interval_end > interval_start)",
            name="ck_operations_interval",
        ),
        CheckConstraint(
            "interval_start IS NULL OR operation_type IN "
            "('artificial_lighting', 'black_nylon')",
            name="ck_operations_interval_type",
        ),
        CheckConstraint(
            "(interval_start IS NULL AND timing_basis IS NULL) "
            "OR (interval_start IS NOT NULL AND timing_basis = 'operator_entered')",
            name="ck_operations_timing_basis",
        ),
        ForeignKeyConstraint(
            ["cycle_id", "vidriera_id"],
            ["cultivation_cycles.id", "cultivation_cycles.vidriera_id"],
            name="fk_operations_cycle_same_vidriera",
        ),
        Index("ix_operations_vidriera_occurred", "vidriera_id", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    vidriera_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("vidrieras.id", ondelete="RESTRICT"),
        nullable=False,
    )
    operation_type: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    cycle_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    origin: Mapped[str] = mapped_column(Text, nullable=False, default="manual")
    interval_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    interval_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    timing_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
