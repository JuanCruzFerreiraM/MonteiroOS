import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.production.models import Cantero, Quinta, Vidriera
from app.modules.production.rules import (
    CANTERO_NUMBERS,
    DomainError,
    display_cantero_code,
    format_vidriera_code,
    name_key,
    normalize_name,
    normalize_notes,
    normalize_optional_name,
    normalize_quinta_code,
    optional_name_key,
    parse_vidriera_code,
)
from app.modules.production.schemas import (
    CanteroRead,
    CanteroUpdate,
    NextVidrieraCode,
    QuintaCreate,
    QuintaRead,
    QuintaUpdate,
    VidrieraCreate,
    VidrieraDetail,
    VidrieraRead,
    VidrieraUpdate,
)

CONSTRAINT_MESSAGES = {
    "uq_quintas_code": "Ya existe una quinta con ese código.",
    "uq_quintas_name": "Ya existe una quinta con ese nombre.",
    "uq_vidrieras_code": "Ya existe una vidriera con ese código.",
    "uq_vidrieras_quinta_number": "Ya existe una vidriera con ese número en la quinta.",
    "uq_vidrieras_quinta_name": "Ya existe una vidriera con ese nombre en la quinta.",
    "uq_canteros_vidriera_number": (
        "Ya existe un cantero con ese número en la vidriera."
    ),
    "uq_canteros_vidriera_name": "Ya existe un cantero con ese nombre en la vidriera.",
}


def list_quintas(session: Session, *, include_inactive: bool) -> list[QuintaRead]:
    statement = select(Quinta).order_by(Quinta.code)
    if not include_inactive:
        statement = statement.where(Quinta.active.is_(True))
    return [_quinta_read(row) for row in session.scalars(statement)]


def create_quinta(session: Session, payload: QuintaCreate) -> QuintaRead:
    quinta = Quinta(
        code=normalize_quinta_code(payload.code),
        name=normalize_name(payload.name),
        name_key=name_key(payload.name),
        notes=normalize_notes(payload.notes),
        active=True,
    )
    return _quinta_read(_commit(session, quinta))


def get_quinta(session: Session, quinta_id: uuid.UUID) -> QuintaRead:
    return _quinta_read(_quinta_or_404(session, quinta_id))


def update_quinta(
    session: Session,
    quinta_id: uuid.UUID,
    payload: QuintaUpdate,
) -> QuintaRead:
    quinta = _quinta_or_404(session, quinta_id)
    fields = payload.model_fields_set
    if "name" in fields:
        if payload.name is None:
            raise DomainError(422, "El nombre es obligatorio.")
        quinta.name = normalize_name(payload.name)
        quinta.name_key = name_key(payload.name)
    if "notes" in fields:
        quinta.notes = normalize_notes(payload.notes)
    if "active" in fields and payload.active is not None:
        quinta.active = payload.active
    return _quinta_read(_commit(session, quinta))


def list_vidrieras(
    session: Session,
    quinta_id: uuid.UUID,
    *,
    include_inactive: bool,
) -> list[VidrieraRead]:
    _quinta_or_404(session, quinta_id)
    statement = (
        select(Vidriera)
        .where(Vidriera.quinta_id == quinta_id)
        .order_by(Vidriera.number)
    )
    if not include_inactive:
        statement = statement.where(Vidriera.active.is_(True))
    return [_vidriera_read(row) for row in session.scalars(statement)]


def suggest_vidriera_code(session: Session, quinta_id: uuid.UUID) -> NextVidrieraCode:
    quinta = _require_active_quinta(session, quinta_id)
    number = _next_number(session, quinta.id)
    return NextVidrieraCode(
        code=format_vidriera_code(quinta.code, number),
        number=number,
    )


def create_vidriera(
    session: Session,
    quinta_id: uuid.UUID,
    payload: VidrieraCreate,
) -> VidrieraDetail:
    quinta = _require_active_quinta(session, quinta_id)
    number = parse_vidriera_code(payload.code, quinta.code)
    vidriera = Vidriera(
        quinta_id=quinta.id,
        code=format_vidriera_code(quinta.code, number),
        number=number,
        name=normalize_name(payload.name),
        name_key=name_key(payload.name),
        notes=normalize_notes(payload.notes),
        active=True,
    )
    try:
        session.add(vidriera)
        session.flush()
        for cantero_number in CANTERO_NUMBERS:
            session.add(
                Cantero(
                    vidriera_id=vidriera.id,
                    number=cantero_number,
                    name=None,
                    name_key=None,
                    active=True,
                )
            )
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise _integrity_error(error) from None
    except Exception:
        session.rollback()
        raise
    session.refresh(vidriera)
    return _vidriera_detail(session, vidriera)


def get_vidriera(session: Session, vidriera_id: uuid.UUID) -> VidrieraDetail:
    vidriera = _vidriera_or_404(session, vidriera_id)
    return _vidriera_detail(session, vidriera)


def update_vidriera(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: VidrieraUpdate,
) -> VidrieraDetail:
    vidriera = _vidriera_or_404(session, vidriera_id)
    fields = payload.model_fields_set
    if "name" in fields:
        if payload.name is None:
            raise DomainError(422, "El nombre es obligatorio.")
        vidriera.name = normalize_name(payload.name)
        vidriera.name_key = name_key(payload.name)
    if "notes" in fields:
        vidriera.notes = normalize_notes(payload.notes)
    if "active" in fields and payload.active is not None:
        if payload.active:
            quinta = _quinta_or_404(session, vidriera.quinta_id)
            if not quinta.active:
                raise DomainError(
                    409,
                    "No se puede activar una vidriera mientras su quinta "
                    "está inactiva.",
                )
        vidriera.active = payload.active
    _commit(session, vidriera)
    return _vidriera_detail(session, vidriera)


def update_cantero(
    session: Session,
    cantero_id: uuid.UUID,
    payload: CanteroUpdate,
) -> CanteroRead:
    cantero = session.get(Cantero, cantero_id)
    if cantero is None:
        raise DomainError(404, "No se encontró el cantero.")
    vidriera = _vidriera_or_404(session, cantero.vidriera_id)
    fields = payload.model_fields_set
    if "name" in fields:
        cantero.name = normalize_optional_name(payload.name)
        cantero.name_key = optional_name_key(payload.name)
    if "active" in fields and payload.active is not None:
        if payload.active and not vidriera.active:
            raise DomainError(
                409,
                "No se puede activar un cantero mientras su vidriera está inactiva.",
            )
        cantero.active = payload.active
    _commit(session, cantero)
    return _cantero_read(cantero, vidriera.code)


def _commit(session: Session, row: Quinta | Vidriera | Cantero):
    try:
        session.add(row)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise _integrity_error(error) from None
    session.refresh(row)
    return row


def _next_number(session: Session, quinta_id: uuid.UUID) -> int:
    current = session.scalar(
        select(func.max(Vidriera.number)).where(Vidriera.quinta_id == quinta_id)
    )
    return (current or 0) + 1


def _require_active_quinta(session: Session, quinta_id: uuid.UUID) -> Quinta:
    quinta = _quinta_or_404(session, quinta_id)
    if not quinta.active:
        raise DomainError(
            409,
            "No se puede crear una vidriera en una quinta inactiva.",
        )
    return quinta


def _quinta_or_404(session: Session, quinta_id: uuid.UUID) -> Quinta:
    quinta = session.get(Quinta, quinta_id)
    if quinta is None:
        raise DomainError(404, "No se encontró la quinta.")
    return quinta


def _vidriera_or_404(session: Session, vidriera_id: uuid.UUID) -> Vidriera:
    vidriera = session.get(Vidriera, vidriera_id)
    if vidriera is None:
        raise DomainError(404, "No se encontró la vidriera.")
    return vidriera


def _vidriera_detail(session: Session, vidriera: Vidriera) -> VidrieraDetail:
    quinta = _quinta_or_404(session, vidriera.quinta_id)
    canteros = session.scalars(
        select(Cantero)
        .where(Cantero.vidriera_id == vidriera.id)
        .order_by(Cantero.number)
    )
    base = _vidriera_read(vidriera).model_dump()
    return VidrieraDetail(
        **base,
        quinta_code=quinta.code,
        quinta_name=quinta.name,
        canteros=[_cantero_read(cantero, vidriera.code) for cantero in canteros],
    )


def _quinta_read(quinta: Quinta) -> QuintaRead:
    return QuintaRead(
        id=quinta.id,
        code=quinta.code,
        name=quinta.name,
        notes=quinta.notes,
        active=quinta.active,
    )


def _vidriera_read(vidriera: Vidriera) -> VidrieraRead:
    return VidrieraRead(
        id=vidriera.id,
        quinta_id=vidriera.quinta_id,
        code=vidriera.code,
        name=vidriera.name,
        notes=vidriera.notes,
        active=vidriera.active,
    )


def _cantero_read(cantero: Cantero, vidriera_code: str) -> CanteroRead:
    return CanteroRead(
        id=cantero.id,
        number=cantero.number,
        display_code=display_cantero_code(vidriera_code, cantero.number),
        name=cantero.name,
        active=cantero.active,
    )


def _integrity_error(error: IntegrityError) -> DomainError:
    constraint = getattr(getattr(error, "orig", None), "diag", None)
    name = getattr(constraint, "constraint_name", None)
    detail = CONSTRAINT_MESSAGES.get(
        name or "",
        "El registro entra en conflicto con uno existente.",
    )
    return DomainError(409, detail)
