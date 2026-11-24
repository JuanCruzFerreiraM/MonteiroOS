import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.operations import records
from app.modules.operations.schemas import (
    OperationCreate,
    OperationRead,
    OperationUpdate,
)

router = APIRouter(prefix="/api/operations", tags=["operations"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get(
    "/vidrieras/{vidriera_id}/operations",
    response_model=list[OperationRead],
)
def list_operations(
    vidriera_id: uuid.UUID,
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[OperationRead]:
    return records.list_operations(session, vidriera_id, limit=limit)


@router.post(
    "/vidrieras/{vidriera_id}/operations",
    response_model=OperationRead,
    status_code=201,
)
def create_operation(
    vidriera_id: uuid.UUID,
    payload: OperationCreate,
    session: DbSession,
) -> OperationRead:
    return records.create_operation(session, vidriera_id, payload)


@router.get("/operations/{operation_id}", response_model=OperationRead)
def get_operation(operation_id: uuid.UUID, session: DbSession) -> OperationRead:
    return records.get_operation(session, operation_id)


@router.patch("/operations/{operation_id}", response_model=OperationRead)
def update_operation(
    operation_id: uuid.UUID,
    payload: OperationUpdate,
    session: DbSession,
) -> OperationRead:
    return records.update_operation(session, operation_id, payload)
