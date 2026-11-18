import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.production import boundaries, services
from app.modules.production.schemas import (
    BoundaryRead,
    BoundaryWrite,
    CanteroRead,
    CanteroUpdate,
    NextVidrieraCode,
    QuintaCreate,
    QuintaMapRead,
    QuintaRead,
    QuintaUpdate,
    VidrieraCreate,
    VidrieraDetail,
    VidrieraRead,
    VidrieraUpdate,
)

router = APIRouter(prefix="/api/production", tags=["production"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/quintas", response_model=list[QuintaRead])
def list_quintas(
    session: DbSession,
    include_inactive: Annotated[bool, Query()] = False,
) -> list[QuintaRead]:
    return services.list_quintas(session, include_inactive=include_inactive)


@router.post("/quintas", response_model=QuintaRead, status_code=201)
def create_quinta(payload: QuintaCreate, session: DbSession) -> QuintaRead:
    return services.create_quinta(session, payload)


@router.get("/quintas/{quinta_id}", response_model=QuintaRead)
def get_quinta(quinta_id: uuid.UUID, session: DbSession) -> QuintaRead:
    return services.get_quinta(session, quinta_id)


@router.patch("/quintas/{quinta_id}", response_model=QuintaRead)
def update_quinta(
    quinta_id: uuid.UUID,
    payload: QuintaUpdate,
    session: DbSession,
) -> QuintaRead:
    return services.update_quinta(session, quinta_id, payload)


@router.get("/quintas/{quinta_id}/vidrieras", response_model=list[VidrieraRead])
def list_vidrieras(
    quinta_id: uuid.UUID,
    session: DbSession,
    include_inactive: Annotated[bool, Query()] = False,
) -> list[VidrieraRead]:
    return services.list_vidrieras(
        session,
        quinta_id,
        include_inactive=include_inactive,
    )


@router.get(
    "/quintas/{quinta_id}/vidrieras/next-code",
    response_model=NextVidrieraCode,
)
def next_vidriera_code(quinta_id: uuid.UUID, session: DbSession) -> NextVidrieraCode:
    return services.suggest_vidriera_code(session, quinta_id)


@router.post(
    "/quintas/{quinta_id}/vidrieras",
    response_model=VidrieraDetail,
    status_code=201,
)
def create_vidriera(
    quinta_id: uuid.UUID,
    payload: VidrieraCreate,
    session: DbSession,
) -> VidrieraDetail:
    return services.create_vidriera(session, quinta_id, payload)


@router.get("/vidrieras/{vidriera_id}", response_model=VidrieraDetail)
def get_vidriera(vidriera_id: uuid.UUID, session: DbSession) -> VidrieraDetail:
    return services.get_vidriera(session, vidriera_id)


@router.patch("/vidrieras/{vidriera_id}", response_model=VidrieraDetail)
def update_vidriera(
    vidriera_id: uuid.UUID,
    payload: VidrieraUpdate,
    session: DbSession,
) -> VidrieraDetail:
    return services.update_vidriera(session, vidriera_id, payload)


@router.get(
    "/quintas/{quinta_id}/boundary",
    response_model=BoundaryRead,
    summary="Read a quinta boundary",
    responses={
        404: {"description": "The quinta does not exist."},
    },
)
def read_quinta_boundary(quinta_id: uuid.UUID, session: DbSession) -> BoundaryRead:
    """Return the saved polygon. An existing quinta without one has geometry null."""
    return boundaries.read_quinta_boundary(session, quinta_id)


@router.put(
    "/quintas/{quinta_id}/boundary",
    response_model=BoundaryRead,
    summary="Save a quinta boundary",
)
def write_quinta_boundary(
    quinta_id: uuid.UUID,
    payload: BoundaryWrite,
    session: DbSession,
) -> BoundaryRead:
    return boundaries.write_quinta_boundary(session, quinta_id, payload)


@router.delete(
    "/quintas/{quinta_id}/boundary",
    status_code=204,
    summary="Remove a quinta boundary",
    responses={404: {"description": "The quinta does not exist."}},
)
def delete_quinta_boundary(quinta_id: uuid.UUID, session: DbSession) -> Response:
    """Clear the geometry and keep the quinta. Missing geometry is still 204."""
    boundaries.clear_quinta_boundary(session, quinta_id)
    return Response(status_code=204)


@router.get(
    "/quintas/{quinta_id}/map",
    response_model=QuintaMapRead,
    summary="Read a quinta map",
)
def read_quinta_map(
    quinta_id: uuid.UUID,
    session: DbSession,
    include_inactive: Annotated[bool, Query()] = False,
) -> QuintaMapRead:
    return boundaries.read_quinta_map(
        session,
        quinta_id,
        include_inactive=include_inactive,
    )


@router.get(
    "/vidrieras/{vidriera_id}/boundary",
    response_model=BoundaryRead,
    summary="Read a vidriera boundary",
    responses={404: {"description": "The vidriera does not exist."}},
)
def read_vidriera_boundary(
    vidriera_id: uuid.UUID,
    session: DbSession,
) -> BoundaryRead:
    """Return the saved polygon. An existing vidriera without one has geometry null."""
    return boundaries.read_vidriera_boundary(session, vidriera_id)


@router.put(
    "/vidrieras/{vidriera_id}/boundary",
    response_model=BoundaryRead,
    summary="Save a vidriera boundary",
)
def write_vidriera_boundary(
    vidriera_id: uuid.UUID,
    payload: BoundaryWrite,
    session: DbSession,
) -> BoundaryRead:
    return boundaries.write_vidriera_boundary(session, vidriera_id, payload)


@router.delete(
    "/vidrieras/{vidriera_id}/boundary",
    status_code=204,
    summary="Remove a vidriera boundary",
    responses={404: {"description": "The vidriera does not exist."}},
)
def delete_vidriera_boundary(vidriera_id: uuid.UUID, session: DbSession) -> Response:
    """Clear the geometry and keep the vidriera. Missing geometry is still 204."""
    boundaries.clear_vidriera_boundary(session, vidriera_id)
    return Response(status_code=204)


@router.patch("/canteros/{cantero_id}", response_model=CanteroRead)
def update_cantero(
    cantero_id: uuid.UUID,
    payload: CanteroUpdate,
    session: DbSession,
) -> CanteroRead:
    return services.update_cantero(session, cantero_id, payload)
