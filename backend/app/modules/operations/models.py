import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    SmallInteger,
    Text,
    Time,
    UniqueConstraint,
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
        CheckConstraint(
            "origin IN ('manual', 'scheduled')",
            name="ck_operations_origin",
        ),
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
            "("
            "origin = 'manual' AND resolution_id IS NULL AND ("
            "(interval_start IS NULL AND timing_basis IS NULL) OR "
            "(interval_start IS NOT NULL AND timing_basis = 'operator_entered')"
            ")"
            ") OR ("
            "origin = 'scheduled' AND resolution_id IS NOT NULL AND "
            "interval_start IS NOT NULL AND timing_basis IN "
            "('operator_entered', 'assumed_from_schedule')"
            ")",
            name="ck_operations_timing_basis",
        ),
        ForeignKeyConstraint(
            ["cycle_id", "vidriera_id"],
            ["cultivation_cycles.id", "cultivation_cycles.vidriera_id"],
            name="fk_operations_cycle_same_vidriera",
        ),
        Index("ix_operations_vidriera_occurred", "vidriera_id", "occurred_at"),
        UniqueConstraint("resolution_id", name="uq_operations_resolution_id"),
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
    resolution_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "occurrence_resolutions.id",
            name="fk_operations_resolution_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )


class RecurringOperationSchedule(Base):
    """One immutable revision of a lighting or black-nylon schedule.

    Revisions that share ``series_id`` are the same schedule over time. A new
    revision starts on its effective date; the previous revision keeps the
    times that already applied. Overlapping periods of the same vidriera and
    type are rejected in the database. ``generates`` is false for a pause, so
    those days are not expected work.
    """

    __tablename__ = "recurring_operation_schedules"
    __table_args__ = (
        CheckConstraint(
            "operation_type IN ('artificial_lighting', 'black_nylon')",
            name="ck_schedules_type",
        ),
        CheckConstraint(
            "effective_end >= effective_start",
            name="ck_schedules_period",
        ),
        CheckConstraint("start_time <> end_time", name="ck_schedules_times"),
        CheckConstraint(
            "status IN ('active', 'paused', 'ended')",
            name="ck_schedules_status",
        ),
        CheckConstraint(
            "cardinality(weekdays) > 0 "
            "AND weekdays <@ ARRAY[1, 2, 3, 4, 5, 6, 7]::smallint[]",
            name="ck_schedules_weekdays",
        ),
        UniqueConstraint(
            "series_id",
            "effective_start",
            name="uq_schedules_series_start",
        ),
        Index(
            "ix_schedules_vidriera_type",
            "vidriera_id",
            "operation_type",
            "effective_start",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    series_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    vidriera_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("vidrieras.id", ondelete="RESTRICT"),
        nullable=False,
    )
    operation_type: Mapped[str] = mapped_column(Text, nullable=False)
    effective_start: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end: Mapped[date] = mapped_column(Date, nullable=False)
    weekdays: Mapped[list[int]] = mapped_column(
        ARRAY(SmallInteger),
        nullable=False,
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    generates: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class OccurrenceResolution(Base):
    """Explicit verification of one expected occurrence.

    Scheduled and unverified occurrences are calculated. This row exists only
    after a person confirms the work or records that it did not happen.
    Expected timestamps stay as they were at confirmation. Actual timestamps
    are stored beside them and can be corrected later.
    """

    __tablename__ = "occurrence_resolutions"
    __table_args__ = (
        UniqueConstraint(
            "series_id",
            "occurrence_date",
            name="uq_resolutions_series_date",
        ),
        CheckConstraint(
            "outcome IN ('confirmed', 'not_occurred')",
            name="ck_resolutions_outcome",
        ),
        CheckConstraint(
            "confirmation_method = 'manual'",
            name="ck_resolutions_method",
        ),
        CheckConstraint(
            "expected_end > expected_start",
            name="ck_resolutions_expected",
        ),
        CheckConstraint(
            "operation_type IN ('artificial_lighting', 'black_nylon')",
            name="ck_resolutions_type",
        ),
        CheckConstraint(
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
        ForeignKeyConstraint(
            ["cycle_id", "vidriera_id"],
            ["cultivation_cycles.id", "cultivation_cycles.vidriera_id"],
            name="fk_resolutions_cycle_same_vidriera",
        ),
        Index("ix_resolutions_vidriera_date", "vidriera_id", "occurrence_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    series_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    occurrence_date: Mapped[date] = mapped_column(Date, nullable=False)
    revision_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("recurring_operation_schedules.id", ondelete="RESTRICT"),
        nullable=False,
    )
    vidriera_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("vidrieras.id", ondelete="RESTRICT"),
        nullable=False,
    )
    operation_type: Mapped[str] = mapped_column(Text, nullable=False)
    expected_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    expected_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    confirmation_method: Mapped[str] = mapped_column(Text, nullable=False)
    timing_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    actual_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cycle_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
