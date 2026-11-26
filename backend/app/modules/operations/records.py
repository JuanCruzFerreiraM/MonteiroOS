import base64
import uuid
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.operations.catalog import (
    INTERVAL_TYPES,
    OPERATION_LABELS,
    require_operation_type,
)
from app.modules.operations.clock import APP_TIMEZONE, reject_future, utc_now
from app.modules.operations.models import (
    OccurrenceResolution,
    Operation,
    RecurringOperationSchedule,
)
from app.modules.operations.schemas import (
    OperationCreate,
    OperationPage,
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
    operation_type: str | None = None,
    start: date | None = None,
    end: date | None = None,
    cycle: str | None = None,
    cursor: str | None = None,
) -> OperationPage:
    """Return completed operations for one vidriera.

    Ordering is occurrence time, then identifier, both descending. The index
    on vidriera and occurrence time supports the date bounds. Rows that share
    a timestamp are ordered by identifier, so a cursor does not skip or repeat
    one. Expectations that were not confirmed are not rows in this table.
    """
    _vidriera_or_404(session, vidriera_id)
    statement = select(Operation).where(Operation.vidriera_id == vidriera_id)
    if operation_type:
        statement = statement.where(
            Operation.operation_type == require_operation_type(operation_type),
        )
    cycle_match = _history_cycle(session, vidriera_id, cycle)
    if cycle_match is not None:
        statement = statement.where(cycle_match)
    lower, upper = _history_bounds(start, end)
    if lower is not None:
        statement = statement.where(Operation.occurred_at >= lower)
    if upper is not None:
        statement = statement.where(Operation.occurred_at < upper)
    if cursor:
        moment, operation_id = _decode_cursor(cursor)
        statement = statement.where(
            or_(
                Operation.occurred_at < moment,
                and_(
                    Operation.occurred_at == moment,
                    Operation.id < operation_id,
                ),
            )
        )
    bounded = min(max(limit, 1), 100)
    rows = list(
        session.scalars(
            statement.order_by(
                Operation.occurred_at.desc(),
                Operation.id.desc(),
            ).limit(bounded + 1)
        ).all()
    )
    visible = rows[:bounded]
    next_cursor = _encode_cursor(visible[-1]) if len(rows) > bounded else None
    return OperationPage(
        items=[_read(row) for row in visible],
        next_cursor=next_cursor,
    )


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
    if "operation_type" in fields and payload.operation_type not in (
        None,
        operation.operation_type,
    ):
        if operation.origin == "scheduled":
            raise DomainError(
                422,
                "La operación programada conserva el tipo de la programación.",
            )
        operation.operation_type = payload.operation_type
    previous_start = operation.interval_start
    previous_end = operation.interval_end
    if "occurred_at" in fields and payload.occurred_at is not None:
        reject_future(payload.occurred_at, "fecha y hora")
        if operation.origin != "scheduled":
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
        new_start = interval[0] if interval else None
        new_end = interval[1] if interval else None
        changed = new_start != previous_start or new_end != previous_end
        operation.interval_start = new_start
        operation.interval_end = new_end
        if operation.origin == "scheduled":
            if changed:
                operation.timing_basis = "operator_entered"
        else:
            operation.timing_basis = "operator_entered" if interval else None
    elif operation.operation_type not in INTERVAL_TYPES:
        operation.interval_start = None
        operation.interval_end = None
        operation.timing_basis = None
    if operation.origin == "scheduled":
        _keep_scheduled_interval(operation)
        _align_scheduled_moment(operation, fields, payload)
        _require_schedule_type(session, operation)
        _sync_resolution(session, operation)
    operation.updated_at = utc_now()
    _commit(session)
    session.refresh(operation)
    return _read(operation)


def _align_scheduled_moment(
    operation: Operation,
    fields: set[str],
    payload: OperationUpdate,
) -> None:
    if (
        "occurred_at" in fields
        and payload.occurred_at is not None
        and payload.occurred_at != operation.interval_start
    ):
        raise DomainError(
            422,
            "En una confirmación programada, la fecha y hora es el inicio real.",
        )
    operation.occurred_at = operation.interval_start


def _require_schedule_type(session: Session, operation: Operation) -> None:
    resolution = (
        None
        if operation.resolution_id is None
        else session.get(OccurrenceResolution, operation.resolution_id)
    )
    revision = (
        None
        if resolution is None
        else session.get(RecurringOperationSchedule, resolution.revision_id)
    )
    if (
        resolution is None
        or revision is None
        or resolution.operation_type != revision.operation_type
        or operation.operation_type != resolution.operation_type
    ):
        raise DomainError(
            422,
            "La operación programada conserva el tipo de la programación.",
        )


def _keep_scheduled_interval(operation: Operation) -> None:
    if operation.operation_type not in INTERVAL_TYPES:
        raise DomainError(
            422,
            "Una confirmación programada sigue siendo iluminación o nylon negro.",
        )
    if operation.interval_start is None or operation.interval_end is None:
        raise DomainError(
            422,
            "La confirmación programada conserva el intervalo real.",
        )


def _sync_resolution(session: Session, operation: Operation) -> None:
    if operation.resolution_id is None:
        return
    resolution = session.get(OccurrenceResolution, operation.resolution_id)
    if resolution is None:
        return
    resolution.actual_start = operation.interval_start
    resolution.actual_end = operation.interval_end
    resolution.timing_basis = operation.timing_basis
    resolution.cycle_id = operation.cycle_id
    resolution.notes = operation.notes


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


def _history_bounds(
    start: date | None,
    end: date | None,
) -> tuple[datetime | None, datetime | None]:
    if start is not None and end is not None and end < start:
        raise DomainError(
            422,
            "La fecha hasta no puede ser anterior a la fecha desde.",
        )
    lower = _local_midnight(start) if start is not None else None
    upper = _local_midnight(end + timedelta(days=1)) if end is not None else None
    return lower, upper


def _local_midnight(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=APP_TIMEZONE)


def _history_cycle(session: Session, vidriera_id: uuid.UUID, cycle: str | None):
    if cycle is None or cycle == "":
        return None
    if cycle == "none":
        return Operation.cycle_id.is_(None)
    try:
        cycle_id = uuid.UUID(cycle)
    except ValueError:
        raise DomainError(422, "El ciclo del historial no es válido.") from None
    _require_cycle(session, vidriera_id, cycle_id)
    return Operation.cycle_id == cycle_id


def _encode_cursor(operation: Operation) -> str:
    instant = operation.occurred_at.astimezone(UTC).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ",
    )
    raw = f"{instant}|{operation.id}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _decode_cursor(value: str) -> tuple[datetime, uuid.UUID]:
    padded = value + "=" * (-len(value) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        instant, operation_id = raw.split("|", 1)
        moment = datetime.strptime(instant, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=UTC,
        )
        return moment, uuid.UUID(operation_id)
    except (ValueError, UnicodeError):
        raise DomainError(422, "El cursor del historial no es válido.") from None


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
        resolution_id=operation.resolution_id,
    )
