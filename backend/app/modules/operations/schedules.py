import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.operations.catalog import OPERATION_LABELS, require_schedule_type
from app.modules.operations.clock import local_today, utc_now
from app.modules.operations.models import (
    OccurrenceResolution,
    Operation,
    RecurringOperationSchedule,
)
from app.modules.operations.recurrence import (
    expected_bounds,
    iter_dates,
    require_period,
    require_range,
    window_has_ended,
)
from app.modules.operations.schedule_schemas import (
    OccurrenceRead,
    ScheduleCreate,
    ScheduleEffectiveFrom,
    ScheduleEnd,
    ScheduleRevise,
    ScheduleRevisionRead,
    ScheduleSeriesRead,
)
from app.modules.production.models import CultivationCycle, Vidriera
from app.modules.production.rules import DomainError, normalize_notes

OVERLAP = "ex_schedules_no_overlap"


def create_schedule(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: ScheduleCreate,
) -> ScheduleSeriesRead:
    _vidriera_or_404(session, vidriera_id)
    now = utc_now()
    revision = RecurringOperationSchedule(
        series_id=uuid.uuid4(),
        vidriera_id=vidriera_id,
        operation_type=payload.operation_type,
        effective_start=payload.effective_start,
        effective_end=payload.effective_end,
        weekdays=payload.weekdays,
        start_time=payload.start_time,
        end_time=payload.end_time,
        notes=normalize_notes(payload.notes),
        status="active",
        generates=True,
        created_at=now,
        updated_at=now,
    )
    session.add(revision)
    _commit(session)
    session.refresh(revision)
    return _series(session, revision.series_id)


def list_schedules(
    session: Session,
    vidriera_id: uuid.UUID,
) -> list[ScheduleSeriesRead]:
    _vidriera_or_404(session, vidriera_id)
    rows = _rows_for_vidriera(session, vidriera_id)
    return [_series_from(rows_for) for rows_for in _grouped(rows).values()]


def get_schedule(session: Session, series_id: uuid.UUID) -> ScheduleSeriesRead:
    return _series(session, series_id)


def revise_schedule(
    session: Session,
    series_id: uuid.UUID,
    payload: ScheduleRevise,
) -> ScheduleSeriesRead:
    current = _mutable(session, series_id)
    _prospective(current, payload.effective_from)
    if payload.effective_end < payload.effective_from:
        raise DomainError(422, "La fecha de fin no puede ser anterior al inicio.")
    saved = _replace(
        session,
        current,
        payload.effective_from,
        {
            "effective_end": payload.effective_end,
            "weekdays": payload.weekdays,
            "start_time": payload.start_time,
            "end_time": payload.end_time,
            "notes": normalize_notes(payload.notes),
        },
    )
    return _series(session, saved.series_id)


def pause_schedule(
    session: Session,
    series_id: uuid.UUID,
    payload: ScheduleEffectiveFrom,
) -> ScheduleSeriesRead:
    current = _mutable(session, series_id)
    if current.status == "paused":
        raise DomainError(409, "La programación ya está en pausa.")
    _prospective(current, payload.effective_from)
    saved = _replace(
        session,
        current,
        payload.effective_from,
        {"status": "paused", "generates": False},
    )
    return _series(session, saved.series_id)


def resume_schedule(
    session: Session,
    series_id: uuid.UUID,
    payload: ScheduleEffectiveFrom,
) -> ScheduleSeriesRead:
    current = _mutable(session, series_id)
    if current.status != "paused":
        raise DomainError(409, "La programación no está en pausa.")
    _prospective(current, payload.effective_from)
    saved = _replace(
        session,
        current,
        payload.effective_from,
        {"status": "active", "generates": True},
    )
    return _series(session, saved.series_id)


def end_schedule(
    session: Session,
    series_id: uuid.UUID,
    payload: ScheduleEnd,
) -> ScheduleSeriesRead:
    current = _current(session, series_id)
    if current.status == "ended":
        raise DomainError(409, "La programación ya finalizó.")
    today = local_today()
    if current.effective_end < today:
        current.status = "ended"
    else:
        if payload.effective_end is None:
            raise DomainError(422, "Indique la fecha de cierre.")
        if payload.effective_end < today:
            raise DomainError(
                422,
                "El cierre no puede borrar días ya transcurridos.",
            )
        if payload.effective_end < current.effective_start:
            raise DomainError(
                422,
                "La fecha de fin no puede ser anterior al inicio.",
            )
        if payload.effective_end > current.effective_end:
            raise DomainError(422, "El cierre no puede extender el período.")
        _reject_resolved_after(session, current.series_id, payload.effective_end)
        current.effective_end = payload.effective_end
        current.status = "ended"
    current.updated_at = utc_now()
    _commit(session)
    return _series(session, current.series_id)


def list_occurrences(
    session: Session,
    vidriera_id: uuid.UUID,
    start: date,
    end: date,
    *,
    operation_type: str | None = None,
    status: str | None = None,
) -> list[OccurrenceRead]:
    _vidriera_or_404(session, vidriera_id)
    require_range(start, end)
    if operation_type is not None:
        operation_type = require_schedule_type(operation_type)
    statement = select(RecurringOperationSchedule).where(
        RecurringOperationSchedule.vidriera_id == vidriera_id,
        RecurringOperationSchedule.generates.is_(True),
        RecurringOperationSchedule.effective_start <= end,
        RecurringOperationSchedule.effective_end >= start,
    )
    if operation_type is not None:
        statement = statement.where(
            RecurringOperationSchedule.operation_type == operation_type
        )
    revisions = session.scalars(statement).all()
    cycles = session.scalars(
        select(CultivationCycle).where(CultivationCycle.vidriera_id == vidriera_id)
    ).all()
    now = utc_now()
    items: list[OccurrenceRead] = []
    for revision in revisions:
        first = max(revision.effective_start, start)
        last = min(revision.effective_end, end)
        if first > last:
            continue
        for day in iter_dates(first, last, list(revision.weekdays)):
            expected_start, expected_end = expected_bounds(
                day,
                revision.start_time,
                revision.end_time,
            )
            state = "unverified" if window_has_ended(expected_end, now) else "scheduled"
            items.append(
                OccurrenceRead(
                    series_id=revision.series_id,
                    revision_id=revision.id,
                    vidriera_id=revision.vidriera_id,
                    occurrence_date=day,
                    operation_type=revision.operation_type,
                    operation_label=OPERATION_LABELS[revision.operation_type],
                    status=state,  # type: ignore[arg-type]
                    expected_start=expected_start,
                    expected_end=expected_end,
                    suggested_cycle_id=_cycle_on(cycles, day),
                )
            )
    items = _with_resolutions(session, vidriera_id, start, end, items)
    if status is not None:
        items = [item for item in items if item.status == status]
    items.sort(key=lambda item: (item.expected_start, item.operation_type))
    return items


def _replace(
    session: Session,
    current: RecurringOperationSchedule,
    effective_from: date,
    changes: dict[str, object],
) -> RecurringOperationSchedule:
    _reject_resolved_from(session, current.series_id, effective_from)
    now = utc_now()
    if current.effective_start >= effective_from:
        for key, value in changes.items():
            setattr(current, key, value)
        require_period(current.effective_start, current.effective_end)
        current.updated_at = now
        _commit(session)
        session.refresh(current)
        return current
    original_end = current.effective_end
    current.effective_end = effective_from - timedelta(days=1)
    current.updated_at = now
    session.flush()
    new_end = changes.get("effective_end", original_end)
    assert isinstance(new_end, date)
    revision = RecurringOperationSchedule(
        series_id=current.series_id,
        vidriera_id=current.vidriera_id,
        operation_type=current.operation_type,
        effective_start=effective_from,
        effective_end=new_end,
        weekdays=list(changes.get("weekdays", current.weekdays)),  # type: ignore[arg-type]
        start_time=changes.get("start_time", current.start_time),  # type: ignore[arg-type]
        end_time=changes.get("end_time", current.end_time),  # type: ignore[arg-type]
        notes=changes.get("notes", current.notes),  # type: ignore[arg-type]
        status=str(changes.get("status", current.status)),
        generates=bool(changes.get("generates", current.generates)),
        created_at=now,
        updated_at=now,
    )
    require_period(revision.effective_start, revision.effective_end)
    session.add(revision)
    _commit(session)
    session.refresh(revision)
    return revision


def _prospective(current: RecurringOperationSchedule, effective_from: date) -> None:
    today = local_today()
    if effective_from < today:
        raise DomainError(
            422,
            "El cambio rige desde hoy o desde una fecha posterior.",
        )
    if effective_from > current.effective_end:
        raise DomainError(422, "La fecha queda fuera del período vigente.")
    if effective_from != today:
        return
    if today.isoweekday() not in set(current.weekdays):
        return
    _, end_at = expected_bounds(today, current.start_time, current.end_time)
    if window_has_ended(end_at, utc_now()):
        raise DomainError(
            422,
            "El turno de hoy ya terminó. El cambio rige desde mañana.",
        )


def _mutable(
    session: Session,
    series_id: uuid.UUID,
) -> RecurringOperationSchedule:
    current = _current(session, series_id)
    if current.status == "ended":
        raise DomainError(409, "La programación ya finalizó.")
    return current


def _current(session: Session, series_id: uuid.UUID) -> RecurringOperationSchedule:
    rows = _rows(session, series_id)
    return max(rows, key=lambda row: (row.effective_start, row.created_at))


def _series(session: Session, series_id: uuid.UUID) -> ScheduleSeriesRead:
    return _series_from(_rows(session, series_id))


def _rows(session: Session, series_id: uuid.UUID) -> list[RecurringOperationSchedule]:
    rows = session.scalars(
        select(RecurringOperationSchedule)
        .where(RecurringOperationSchedule.series_id == series_id)
        .order_by(RecurringOperationSchedule.effective_start)
    ).all()
    if not rows:
        raise DomainError(404, "No se encontró la programación.")
    return list(rows)


def _rows_for_vidriera(
    session: Session,
    vidriera_id: uuid.UUID,
) -> list[RecurringOperationSchedule]:
    return list(
        session.scalars(
            select(RecurringOperationSchedule)
            .where(RecurringOperationSchedule.vidriera_id == vidriera_id)
            .order_by(RecurringOperationSchedule.effective_start)
        ).all()
    )


def _grouped(
    rows: list[RecurringOperationSchedule],
) -> dict[uuid.UUID, list[RecurringOperationSchedule]]:
    grouped: dict[uuid.UUID, list[RecurringOperationSchedule]] = {}
    for row in rows:
        grouped.setdefault(row.series_id, []).append(row)
    return grouped


def _series_from(rows: list[RecurringOperationSchedule]) -> ScheduleSeriesRead:
    ordered = sorted(rows, key=lambda row: row.effective_start)
    current = max(ordered, key=lambda row: (row.effective_start, row.created_at))
    return ScheduleSeriesRead(
        series_id=current.series_id,
        current=_read_revision(current),
        revisions=[_read_revision(row) for row in ordered],
    )


def _read_revision(row: RecurringOperationSchedule) -> ScheduleRevisionRead:
    return ScheduleRevisionRead(
        id=row.id,
        series_id=row.series_id,
        vidriera_id=row.vidriera_id,
        operation_type=row.operation_type,
        operation_label=OPERATION_LABELS[row.operation_type],
        effective_start=row.effective_start,
        effective_end=row.effective_end,
        weekdays=list(row.weekdays),
        start_time=row.start_time,
        end_time=row.end_time,
        notes=row.notes,
        status=row.status,  # type: ignore[arg-type]
        generates=row.generates,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _with_resolutions(
    session: Session,
    vidriera_id: uuid.UUID,
    start: date,
    end: date,
    items: list[OccurrenceRead],
) -> list[OccurrenceRead]:
    resolutions = session.scalars(
        select(OccurrenceResolution).where(
            OccurrenceResolution.vidriera_id == vidriera_id,
            OccurrenceResolution.occurrence_date >= start,
            OccurrenceResolution.occurrence_date <= end,
        )
    ).all()
    if not resolutions:
        return items
    operations = session.scalars(
        select(Operation).where(
            Operation.resolution_id.in_([row.id for row in resolutions])
        )
    ).all()
    by_resolution = {row.resolution_id: row for row in operations}
    by_key = {(row.series_id, row.occurrence_date): row for row in resolutions}
    overlaid: list[OccurrenceRead] = []
    for item in items:
        resolution = by_key.get((item.series_id, item.occurrence_date))
        if resolution is None:
            overlaid.append(item)
            continue
        operation = by_resolution.get(resolution.id)
        overlaid.append(
            item.model_copy(
                update={
                    "revision_id": resolution.revision_id,
                    "status": resolution.outcome,
                    "expected_start": resolution.expected_start,
                    "expected_end": resolution.expected_end,
                    "actual_start": resolution.actual_start,
                    "actual_end": resolution.actual_end,
                    "timing_basis": resolution.timing_basis,
                    "confirmation_method": resolution.confirmation_method,
                    "cycle_id": resolution.cycle_id,
                    "notes": resolution.notes,
                    "operation_id": None if operation is None else operation.id,
                }
            )
        )
    return overlaid


def _reject_resolved_from(session: Session, series_id: uuid.UUID, day: date) -> None:
    found = session.scalar(
        select(OccurrenceResolution.id).where(
            OccurrenceResolution.series_id == series_id,
            OccurrenceResolution.occurrence_date >= day,
        )
    )
    if found is not None:
        raise DomainError(
            409,
            "Hay confirmaciones desde esa fecha. El cambio no las reescribe.",
        )


def _reject_resolved_after(session: Session, series_id: uuid.UUID, day: date) -> None:
    found = session.scalar(
        select(OccurrenceResolution.id).where(
            OccurrenceResolution.series_id == series_id,
            OccurrenceResolution.occurrence_date > day,
        )
    )
    if found is not None:
        raise DomainError(
            409,
            "Hay confirmaciones desde esa fecha. El cambio no las reescribe.",
        )


def _cycle_on(cycles: list[CultivationCycle], day: date) -> uuid.UUID | None:
    for cycle in cycles:
        if cycle.start_date <= day and (
            cycle.end_date is None or day <= cycle.end_date
        ):
            return cycle.id
    return None


def _vidriera_or_404(session: Session, vidriera_id: uuid.UUID) -> Vidriera:
    vidriera = session.get(Vidriera, vidriera_id)
    if vidriera is None:
        raise DomainError(404, "No se encontró la vidriera.")
    return vidriera


def _commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        diagnostic = getattr(getattr(error, "orig", None), "diag", None)
        name = getattr(diagnostic, "constraint_name", None)
        if name == OVERLAP:
            raise DomainError(
                409,
                "Ya hay una programación de este tipo en esas fechas. "
                "No se reemplaza sola.",
            ) from None
        raise DomainError(
            409,
            "La programación entra en conflicto con un registro existente.",
        ) from None
    except Exception:
        session.rollback()
        raise
