"""Confirm or reject expected occurrences.

One transaction handles a batch. Each item runs inside a savepoint, so a
conflict or a validation error rolls back only that item. HTTP 200 means the
batch was processed. It does not mean every item succeeded. A repeated request
with the same outcome is idempotent and does not overwrite actual times.
Corrections go through the operation update.
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.operations.clock import reject_future, utc_now
from app.modules.operations.models import (
    OccurrenceResolution,
    Operation,
    RecurringOperationSchedule,
)
from app.modules.operations.records import _require_cycle
from app.modules.operations.recurrence import expected_bounds, window_has_ended
from app.modules.operations.resolution_schemas import (
    MAX_BATCH,
    BatchResolve,
    OccurrenceResolve,
    ResolveResult,
)
from app.modules.production.rules import DomainError, normalize_notes


def resolve_one(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: OccurrenceResolve,
) -> ResolveResult:
    try:
        result = _apply(session, vidriera_id, payload)
        session.commit()
    except DomainError:
        session.rollback()
        raise
    except IntegrityError:
        session.rollback()
        raise DomainError(409, "La ocurrencia ya fue resuelta.") from None
    return result


def resolve_batch(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: BatchResolve,
) -> list[ResolveResult]:
    if not payload.items:
        raise DomainError(422, "La confirmación no incluye ocurrencias.")
    if len(payload.items) > MAX_BATCH:
        raise DomainError(422, "Se pueden resolver hasta 31 ocurrencias por vez.")
    results: list[ResolveResult] = []
    for item in payload.items:
        nested = session.begin_nested()
        try:
            results.append(_apply(session, vidriera_id, item))
            nested.commit()
        except DomainError as error:
            nested.rollback()
            results.append(_failed(item, error))
        except IntegrityError:
            nested.rollback()
            results.append(
                _failed(item, DomainError(409, "La ocurrencia ya fue resuelta."))
            )
    session.commit()
    return results


def _apply(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: OccurrenceResolve,
) -> ResolveResult:
    revision = _revision(session, vidriera_id, payload)
    expected_start, expected_end = expected_bounds(
        payload.occurrence_date,
        revision.start_time,
        revision.end_time,
    )
    if not window_has_ended(expected_end, utc_now()):
        raise DomainError(
            422,
            "La ocurrencia todavía no terminó. No se confirma por adelantado.",
        )
    existing = session.scalar(
        select(OccurrenceResolution).where(
            OccurrenceResolution.series_id == payload.series_id,
            OccurrenceResolution.occurrence_date == payload.occurrence_date,
        )
    )
    if existing is not None:
        if existing.outcome == payload.outcome:
            operation = session.scalar(
                select(Operation).where(Operation.resolution_id == existing.id)
            )
            return ResolveResult(
                series_id=payload.series_id,
                occurrence_date=payload.occurrence_date,
                status="unchanged",
                message="La ocurrencia ya estaba resuelta.",
                operation_id=None if operation is None else operation.id,
                resolution_id=existing.id,
            )
        raise DomainError(409, "La ocurrencia ya fue resuelta.")
    _require_cycle(session, vidriera_id, payload.cycle_id)
    actual_start, actual_end, basis = _actual_times(
        payload,
        expected_start,
        expected_end,
    )
    now = utc_now()
    resolution = OccurrenceResolution(
        series_id=revision.series_id,
        occurrence_date=payload.occurrence_date,
        revision_id=revision.id,
        vidriera_id=vidriera_id,
        operation_type=revision.operation_type,
        expected_start=expected_start,
        expected_end=expected_end,
        outcome=payload.outcome,
        confirmation_method="manual",
        timing_basis=basis,
        actual_start=actual_start,
        actual_end=actual_end,
        cycle_id=payload.cycle_id,
        notes=normalize_notes(payload.notes),
        confirmed_at=now,
    )
    session.add(resolution)
    session.flush()
    operation_id = None
    if payload.outcome == "confirmed":
        assert actual_start is not None and actual_end is not None
        operation = Operation(
            vidriera_id=vidriera_id,
            operation_type=revision.operation_type,
            occurred_at=actual_start,
            cycle_id=payload.cycle_id,
            notes=resolution.notes,
            recorded_at=now,
            updated_at=now,
            origin="scheduled",
            interval_start=actual_start,
            interval_end=actual_end,
            timing_basis=basis,
            resolution_id=resolution.id,
        )
        session.add(operation)
        session.flush()
        operation_id = operation.id
    return ResolveResult(
        series_id=payload.series_id,
        occurrence_date=payload.occurrence_date,
        status=payload.outcome,
        operation_id=operation_id,
        resolution_id=resolution.id,
    )


def _revision(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: OccurrenceResolve,
) -> RecurringOperationSchedule:
    revision = session.scalar(
        select(RecurringOperationSchedule).where(
            RecurringOperationSchedule.series_id == payload.series_id,
            RecurringOperationSchedule.vidriera_id == vidriera_id,
            RecurringOperationSchedule.generates.is_(True),
            RecurringOperationSchedule.effective_start <= payload.occurrence_date,
            RecurringOperationSchedule.effective_end >= payload.occurrence_date,
        )
    )
    if revision is None or payload.occurrence_date.isoweekday() not in set(
        revision.weekdays
    ):
        raise DomainError(404, "No hay una ocurrencia esperada en esa fecha.")
    return revision


def _actual_times(
    payload: OccurrenceResolve,
    expected_start: datetime,
    expected_end: datetime,
) -> tuple[datetime | None, datetime | None, str | None]:
    if payload.outcome == "not_occurred":
        if payload.actual_start is not None or payload.actual_end is not None:
            raise DomainError(
                422,
                "Una ocurrencia que no se realizó no tiene horario real.",
            )
        return None, None, None
    basis = payload.timing_basis
    if basis is None:
        sent = payload.actual_start is not None or payload.actual_end is not None
        basis = "operator_entered" if sent else "assumed_from_schedule"
    if basis == "assumed_from_schedule":
        if _differs(payload.actual_start, expected_start) or _differs(
            payload.actual_end,
            expected_end,
        ):
            raise DomainError(
                422,
                "El horario supuesto tiene que coincidir con la programación.",
            )
        return expected_start, expected_end, basis
    if payload.actual_start is None or payload.actual_end is None:
        raise DomainError(422, "Indique el inicio y el fin reales.")
    if payload.actual_end <= payload.actual_start:
        raise DomainError(422, "El fin real tiene que ser posterior al inicio.")
    reject_future(payload.actual_end, "fin real")
    return payload.actual_start, payload.actual_end, "operator_entered"


def _differs(sent: datetime | None, expected: datetime) -> bool:
    return sent is not None and sent != expected


def _failed(item: OccurrenceResolve, error: DomainError) -> ResolveResult:
    status = "conflict" if error.status_code == 409 else "invalid"
    return ResolveResult(
        series_id=item.series_id,
        occurrence_date=item.occurrence_date,
        status=status,
        message=error.detail,
    )
