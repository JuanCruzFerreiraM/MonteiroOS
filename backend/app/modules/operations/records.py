import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.operations.catalog import INTERVAL_TYPES, OPERATION_LABELS
from app.modules.operations.clock import reject_future, utc_now
from app.modules.operations.models import Operation
from app.modules.operations.schemas import (
    OperationCreate,
    OperationRead,
    OperationUpdate,
)
from app.modules.production.models import CultivationCycle, Vidriera
from app.modules.production.rules import DomainError, normalize_notes

CYCLE_VIDRIERA_FK = "fk_operations_cycle_same_vidriera"
VIDRIERA_FK = "fk_operations_vidriera_id"


def list_operations(
    session: Session,
    vidriera_id: uuid.UUID,
    *,
    limit: int = 50,
) -> list[OperationRead]:
    _vidriera_or_404(session, vidriera_id)
    bounded = min(max(limit, 1), 100)
    rows = session.scalars(
        select(Operation)
        .where(Operation.vidriera_id == vidriera_id)
        .order_by(Operation.occurred_at.desc(), Operation.id.desc())
        .limit(bounded)
    ).all()
    return [_read(row) for row in rows]


def get_operation(session: Session, operation_id: uuid.UUID) -> OperationRead:
    return _read(_operation_or_404(session, operation_id))


def create_operation(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: OperationCreate,
) -> OperationRead:
    _vidriera_or_404(session, vidriera_id)
    _require_cycle(session, vidriera_id, payload.cycle_id)
    interval = _completed_interval(
        payload.operation_type,
        payload.interval_start,
        payload.interval_end,
    )
    reject_future(payload.occurred_at, "fecha y hora")
    now = utc_now()
    operation = Operation(
        vidriera_id=vidriera_id,
        operation_type=payload.operation_type,
        occurred_at=payload.occurred_at,
        cycle_id=payload.cycle_id,
        notes=normalize_notes(payload.notes),
        recorded_at=now,
        updated_at=now,
        origin="manual",
        interval_start=interval[0] if interval else None,
        interval_end=interval[1] if interval else None,
        timing_basis="operator_entered" if interval else None,
    )
    session.add(operation)
    _commit(session)
    session.refresh(operation)
    return _read(operation)


def update_operation(
    session: Session,
    operation_id: uuid.UUID,
    payload: OperationUpdate,
) -> OperationRead:
    operation = _operation_or_404(session, operation_id)
    fields = payload.model_fields_set
    if not fields:
        raise DomainError(422, "No hay cambios para guardar.")
    if "operation_type" in fields and payload.operation_type is not None:
        operation.operation_type = payload.operation_type
    if "occurred_at" in fields and payload.occurred_at is not None:
        reject_future(payload.occurred_at, "fecha y hora")
        operation.occurred_at = payload.occurred_at
    if "cycle_id" in fields:
        _require_cycle(session, operation.vidriera_id, payload.cycle_id)
        operation.cycle_id = payload.cycle_id
    if "notes" in fields:
        operation.notes = normalize_notes(payload.notes)
    if "interval_start" in fields or "interval_end" in fields:
        start = (
            payload.interval_start
            if "interval_start" in fields
            else operation.interval_start
        )
        end = (
            payload.interval_end if "interval_end" in fields else operation.interval_end
        )
        interval = _completed_interval(operation.operation_type, start, end)
        operation.interval_start = interval[0] if interval else None
        operation.interval_end = interval[1] if interval else None
        operation.timing_basis = "operator_entered" if interval else None
    elif operation.operation_type not in INTERVAL_TYPES:
        operation.interval_start = None
        operation.interval_end = None
        operation.timing_basis = None
    operation.updated_at = utc_now()
    _commit(session)
    session.refresh(operation)
    return _read(operation)


def _completed_interval(
    operation_type: str,
    start: datetime | None,
    end: datetime | None,
) -> tuple[datetime, datetime] | None:
    if start is None and end is None:
        return None
    if operation_type not in INTERVAL_TYPES:
        raise DomainError(
            422,
            "El intervalo real solo corresponde a iluminación o nylon negro.",
        )
    if start is None or end is None:
        raise DomainError(422, "El intervalo real necesita inicio y fin.")
    if end <= start:
        raise DomainError(422, "El fin real tiene que ser posterior al inicio.")
    reject_future(end, "fin real")
    return start, end


def _require_cycle(
    session: Session,
    vidriera_id: uuid.UUID,
    cycle_id: uuid.UUID | None,
) -> None:
    if cycle_id is None:
        return
    cycle = session.get(CultivationCycle, cycle_id)
    if cycle is None or cycle.vidriera_id != vidriera_id:
        raise DomainError(422, "El ciclo no pertenece a esta vidriera.")


def _vidriera_or_404(session: Session, vidriera_id: uuid.UUID) -> Vidriera:
    vidriera = session.get(Vidriera, vidriera_id)
    if vidriera is None:
        raise DomainError(404, "No se encontró la vidriera.")
    return vidriera


def _operation_or_404(session: Session, operation_id: uuid.UUID) -> Operation:
    operation = session.get(Operation, operation_id)
    if operation is None:
        raise DomainError(404, "No se encontró la operación.")
    return operation


def _commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise _integrity(error) from None
    except Exception:
        session.rollback()
        raise


def _integrity(error: IntegrityError) -> DomainError:
    diagnostic = getattr(getattr(error, "orig", None), "diag", None)
    name = getattr(diagnostic, "constraint_name", None)
    if name == CYCLE_VIDRIERA_FK:
        return DomainError(422, "El ciclo no pertenece a esta vidriera.")
    if name == VIDRIERA_FK:
        return DomainError(404, "No se encontró la vidriera.")
    return DomainError(
        409,
        "La operación entra en conflicto con un registro existente.",
    )


def _read(operation: Operation) -> OperationRead:
    return OperationRead(
        id=operation.id,
        vidriera_id=operation.vidriera_id,
        operation_type=operation.operation_type,
        operation_label=OPERATION_LABELS[operation.operation_type],
        occurred_at=operation.occurred_at,
        cycle_id=operation.cycle_id,
        notes=operation.notes,
        recorded_at=operation.recorded_at,
        updated_at=operation.updated_at,
        origin=operation.origin,  # type: ignore[arg-type]
        interval_start=operation.interval_start,
        interval_end=operation.interval_end,
        timing_basis=operation.timing_basis,  # type: ignore[arg-type]
    )
