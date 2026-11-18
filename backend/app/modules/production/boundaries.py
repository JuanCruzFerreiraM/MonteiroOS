import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.production.geometry import (
    GeometryWarning,
    parse_polygon,
    read_vidriera_warnings,
    require_vidriera_placement,
)
from app.modules.production.models import Quinta, Vidriera
from app.modules.production.rules import DomainError
from app.modules.production.schemas import (
    BoundaryRead,
    BoundaryWarningRead,
    BoundaryWrite,
    MapVidrieraRead,
    QuintaMapRead,
)


def read_quinta_boundary(session: Session, quinta_id: uuid.UUID) -> BoundaryRead:
    quinta = _quinta_or_404(session, quinta_id)
    return _boundary_read(quinta.id, quinta.boundary, [])


def write_quinta_boundary(
    session: Session,
    quinta_id: uuid.UUID,
    payload: BoundaryWrite,
) -> BoundaryRead:
    quinta = _quinta_or_404(session, quinta_id)
    _reject_attach_when_present(payload.mode, quinta.boundary, "quinta")
    geometry = parse_polygon(payload.geometry)
    quinta.boundary = geometry
    _save(session, quinta)
    return _boundary_read(quinta.id, geometry, [])


def clear_quinta_boundary(session: Session, quinta_id: uuid.UUID) -> None:
    quinta = _quinta_or_404(session, quinta_id)
    quinta.boundary = None
    _save(session, quinta)


def read_vidriera_boundary(session: Session, vidriera_id: uuid.UUID) -> BoundaryRead:
    vidriera = _vidriera_or_404(session, vidriera_id)
    warnings = _warnings_for(session, vidriera)
    return _boundary_read(vidriera.id, vidriera.boundary, warnings)


def write_vidriera_boundary(
    session: Session,
    vidriera_id: uuid.UUID,
    payload: BoundaryWrite,
) -> BoundaryRead:
    vidriera = _vidriera_or_404(session, vidriera_id)
    quinta = _quinta_or_404(session, vidriera.quinta_id)
    if quinta.boundary is None:
        raise DomainError(
            409,
            "Dibuje primero el límite de la quinta. La vidriera puede crearse "
            "igual desde el listado, sin polígono.",
        )
    _reject_attach_when_present(payload.mode, vidriera.boundary, "vidriera")
    geometry = parse_polygon(payload.geometry)
    warnings = require_vidriera_placement(
        geometry,
        quinta.boundary,
        _other_boundaries(session, quinta.id, vidriera.id),
    )
    vidriera.boundary = geometry
    _save(session, vidriera)
    return _boundary_read(vidriera.id, geometry, warnings)


def clear_vidriera_boundary(session: Session, vidriera_id: uuid.UUID) -> None:
    vidriera = _vidriera_or_404(session, vidriera_id)
    vidriera.boundary = None
    _save(session, vidriera)


def read_quinta_map(
    session: Session,
    quinta_id: uuid.UUID,
    *,
    include_inactive: bool,
) -> QuintaMapRead:
    quinta = _quinta_or_404(session, quinta_id)
    statement = (
        select(Vidriera)
        .where(Vidriera.quinta_id == quinta.id)
        .order_by(Vidriera.number)
    )
    if not include_inactive:
        statement = statement.where(Vidriera.active.is_(True))
    vidrieras = list(session.scalars(statement))
    return QuintaMapRead(
        id=quinta.id,
        code=quinta.code,
        name=quinta.name,
        active=quinta.active,
        geometry=quinta.boundary,
        vidrieras=[
            MapVidrieraRead(
                id=vidriera.id,
                code=vidriera.code,
                name=vidriera.name,
                active=vidriera.active,
                geometry=vidriera.boundary,
                warnings=_warning_reads(_warnings_for(session, vidriera)),
            )
            for vidriera in vidrieras
        ],
    )


def _warnings_for(session: Session, vidriera: Vidriera) -> list[GeometryWarning]:
    if vidriera.boundary is None:
        return []
    quinta = _quinta_or_404(session, vidriera.quinta_id)
    return read_vidriera_warnings(
        vidriera.boundary,
        quinta.boundary,
        _other_boundaries(session, quinta.id, vidriera.id),
    )


def _other_boundaries(
    session: Session,
    quinta_id: uuid.UUID,
    vidriera_id: uuid.UUID,
) -> list[tuple[uuid.UUID, str, dict]]:
    rows = session.scalars(select(Vidriera).where(Vidriera.quinta_id == quinta_id))
    return [
        (row.id, row.code, row.boundary)
        for row in rows
        if row.id != vidriera_id and row.boundary is not None
    ]


def _reject_attach_when_present(mode: str, boundary: dict | None, kind: str) -> None:
    if mode == "attach" and boundary is not None:
        raise DomainError(
            409,
            f"Esta {kind} ya tiene un límite. Edítelo para reemplazarlo; "
            "no se adjuntó otro polígono.",
        )


def _boundary_read(
    entity_id: uuid.UUID,
    geometry: dict | None,
    warnings: list[GeometryWarning],
) -> BoundaryRead:
    return BoundaryRead(
        id=entity_id,
        geometry=geometry,
        warnings=_warning_reads(warnings),
    )


def _warning_reads(warnings: list[GeometryWarning]) -> list[BoundaryWarningRead]:
    return [
        BoundaryWarningRead(
            code=warning.code,
            message=warning.message,
            vidriera_id=warning.vidriera_id,
            vidriera_code=warning.vidriera_code,
        )
        for warning in warnings
    ]


def _save(session: Session, row: Quinta | Vidriera) -> None:
    try:
        session.add(row)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise DomainError(409, "No se pudo guardar el límite.") from None
    except Exception:
        session.rollback()
        raise
    session.refresh(row)


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
