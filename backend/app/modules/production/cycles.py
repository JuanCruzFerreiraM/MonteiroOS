import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.production.models import CultivationCycle, Vidriera
from app.modules.production.rules import (
    DomainError,
    cycle_status,
    normalize_notes,
    periods_overlap,
)
from app.modules.production.schemas import (
    CycleCollection,
    CycleCorrection,
    CycleFinalize,
    CycleRead,
    CycleStart,
)

ACTIVE_CYCLE_INDEX = "uq_cultivation_cycles_one_active"
OVERLAP_CONSTRAINT = "ex_cultivation_cycles_no_overlap"
END_BEFORE_START = "ck_cultivation_cycles_end_not_before_start"
VIDRIERA_FOREIGN_KEY = "fk_cultivation_cycles_vidriera_id"


def list_cycles(session: Session, vidriera_id: uuid.UUID) -> CycleCollection:
    _vidriera_or_404(session, vidriera_id)
    rows = session.scalars(
        select(CultivationCycle)
        .where(CultivationCycle.vidriera_id == vidriera_id)
        .order_by(CultivationCycle.start_date.desc(), CultivationCycle.id.desc())
    ).all()
    active = next((row for row in rows if row.end_date is None), None)
    history = [row for row in rows if row.end_date is not None]
    return CycleCollection(
        active=_read(active) if active is not None else None,
        history=[_read(row) for row in history],
    )


def get_active_cycle(session: Session, vidriera_id: uuid.UUID) -> CycleRead:
    _vidriera_or_404(session, vidriera_id)
    cycle = _load_active(session, vidriera_id)
    if cycle is None:
        raise DomainError(404, "Esta vidriera no tiene un ciclo activo.")
    return _read(cycle)


def get_cycle(session: Session, cycle_id: uuid.UUID) -> CycleRead:
    return _read(_cycle_or_404(session, cycle_id))


def start_cycle(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: CycleStart,
) -> CycleRead:
    _vidriera_or_404(session, vidriera_id)
    _reject_known_conflicts(
        session,
        vidriera_id,
        payload.start_date,
        None,
        None,
        active_blocks=True,
    )
    cycle = CultivationCycle(
        vidriera_id=vidriera_id,
        start_date=payload.start_date,
        end_date=None,
        notes=normalize_notes(payload.notes),
    )
    session.add(cycle)
    _commit(session, vidriera_id, payload.start_date, None, None)
    session.refresh(cycle)
    return _read(cycle)


def finalize_cycle(
    session: Session,
    cycle_id: uuid.UUID,
    payload: CycleFinalize,
) -> CycleRead:
    cycle = _cycle_or_404(session, cycle_id)
    if cycle.end_date is not None:
        raise DomainError(409, "Este ciclo ya está finalizado.")
    if payload.end_date < cycle.start_date:
        raise DomainError(
            422,
            "La fecha de cierre no puede ser anterior a la plantación.",
        )
    _reject_known_conflicts(
        session,
        cycle.vidriera_id,
        cycle.start_date,
        payload.end_date,
        cycle.id,
        active_blocks=False,
    )
    cycle.end_date = payload.end_date
    _commit(
        session,
        cycle.vidriera_id,
        cycle.start_date,
        payload.end_date,
        cycle.id,
    )
    session.refresh(cycle)
    return _read(cycle)


def correct_cycle(
    session: Session,
    cycle_id: uuid.UUID,
    payload: CycleCorrection,
) -> CycleRead:
    cycle = _cycle_or_404(session, cycle_id)
    fields = payload.model_fields_set
    if not fields:
        raise DomainError(422, "No hay cambios para guardar.")
    if cycle.end_date is None and "end_date" in fields:
        raise DomainError(
            409,
            "Un ciclo activo se cierra al finalizarlo, no al corregirlo.",
        )
    if cycle.end_date is not None and "end_date" in fields and payload.end_date is None:
        raise DomainError(409, "Una corrección no reabre un ciclo finalizado.")
    if "start_date" in fields and payload.start_date is None:
        raise DomainError(422, "La fecha de plantación es obligatoria.")

    new_start = cycle.start_date
    if "start_date" in fields and payload.start_date is not None:
        new_start = payload.start_date
    new_end = cycle.end_date
    if cycle.end_date is not None and "end_date" in fields:
        new_end = payload.end_date
    if new_end is not None and new_end < new_start:
        raise DomainError(
            422,
            "La fecha de cierre no puede ser anterior a la plantación.",
        )
    if new_start != cycle.start_date or new_end != cycle.end_date:
        _reject_known_conflicts(
            session,
            cycle.vidriera_id,
            new_start,
            new_end,
            cycle.id,
            active_blocks=False,
        )
        cycle.start_date = new_start
        cycle.end_date = new_end
    if "notes" in fields:
        cycle.notes = normalize_notes(payload.notes)
    _commit(session, cycle.vidriera_id, new_start, new_end, cycle.id)
    session.refresh(cycle)
    return _read(cycle)


def _reject_known_conflicts(
    session: Session,
    vidriera_id: uuid.UUID,
    start: date,
    end: date | None,
    ignore_id: uuid.UUID | None,
    *,
    active_blocks: bool,
) -> None:
    if active_blocks:
        active = _load_active(session, vidriera_id)
        if active is not None and active.id != ignore_id:
            raise DomainError(409, _active_message(active))
    overlap = _load_overlap(session, vidriera_id, start, end, ignore_id)
    if overlap is not None:
        raise DomainError(409, _overlap_message(overlap))


def _commit(
    session: Session,
    vidriera_id: uuid.UUID,
    start: date,
    end: date | None,
    ignore_id: uuid.UUID | None,
) -> None:
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise _integrity_error(
            session,
            vidriera_id,
            start,
            end,
            ignore_id,
            error,
        ) from None
    except Exception:
        session.rollback()
        raise


def _integrity_error(
    session: Session,
    vidriera_id: uuid.UUID,
    start: date,
    end: date | None,
    ignore_id: uuid.UUID | None,
    error: IntegrityError,
) -> DomainError:
    diagnostic = getattr(getattr(error, "orig", None), "diag", None)
    name = getattr(diagnostic, "constraint_name", None)
    if name == ACTIVE_CYCLE_INDEX:
        active = _load_active(session, vidriera_id)
        if active is not None:
            return DomainError(409, _active_message(active))
        return DomainError(409, "Esta vidriera ya tiene un ciclo activo.")
    if name == OVERLAP_CONSTRAINT:
        overlap = _load_overlap(session, vidriera_id, start, end, ignore_id)
        if overlap is not None:
            return DomainError(409, _overlap_message(overlap))
        return DomainError(
            409,
            "El período se superpone con otro ciclo de esta vidriera.",
        )
    if name == END_BEFORE_START:
        return DomainError(
            422,
            "La fecha de cierre no puede ser anterior a la plantación.",
        )
    if name == VIDRIERA_FOREIGN_KEY:
        return DomainError(404, "No se encontró la vidriera.")
    return DomainError(409, "El ciclo entra en conflicto con uno existente.")


def _load_active(session: Session, vidriera_id: uuid.UUID) -> CultivationCycle | None:
    return session.scalar(
        select(CultivationCycle).where(
            CultivationCycle.vidriera_id == vidriera_id,
            CultivationCycle.end_date.is_(None),
        )
    )


def _load_overlap(
    session: Session,
    vidriera_id: uuid.UUID,
    start: date,
    end: date | None,
    ignore_id: uuid.UUID | None,
) -> CultivationCycle | None:
    rows = session.scalars(
        select(CultivationCycle)
        .where(CultivationCycle.vidriera_id == vidriera_id)
        .order_by(CultivationCycle.start_date, CultivationCycle.id)
    ).all()
    for row in rows:
        if ignore_id is not None and row.id == ignore_id:
            continue
        if periods_overlap(start, end, row.start_date, row.end_date):
            return row
    return None


def _vidriera_or_404(session: Session, vidriera_id: uuid.UUID) -> Vidriera:
    vidriera = session.get(Vidriera, vidriera_id)
    if vidriera is None:
        raise DomainError(404, "No se encontró la vidriera.")
    return vidriera


def _cycle_or_404(session: Session, cycle_id: uuid.UUID) -> CultivationCycle:
    cycle = session.get(CultivationCycle, cycle_id)
    if cycle is None:
        raise DomainError(404, "No se encontró el ciclo.")
    return cycle


def _read(cycle: CultivationCycle) -> CycleRead:
    return CycleRead(
        id=cycle.id,
        vidriera_id=cycle.vidriera_id,
        start_date=cycle.start_date,
        end_date=cycle.end_date,
        status=cycle_status(cycle.end_date),
        notes=cycle.notes,
    )


def _active_message(cycle: CultivationCycle) -> str:
    return (
        "Esta vidriera ya tiene un ciclo activo "
        f"desde {cycle.start_date.isoformat()} ({cycle.id}). "
        "Finalícelo antes de empezar otro."
    )


def _overlap_message(cycle: CultivationCycle) -> str:
    if cycle.end_date is None:
        span = f"{cycle.start_date.isoformat()} – sin cierre"
    else:
        span = f"{cycle.start_date.isoformat()} – {cycle.end_date.isoformat()}"
    return f"El período se superpone con el ciclo {cycle.id} ({span})."
