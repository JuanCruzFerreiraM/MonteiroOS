import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.operations import records, resolutions, schedules
from app.modules.operations.resolution_schemas import (
    BatchResolve,
    OccurrenceResolve,
    ResolveResult,
)
from app.modules.operations.schedule_schemas import (
    OccurrenceRead,
    ScheduleCreate,
    ScheduleEffectiveFrom,
    ScheduleEnd,
    ScheduleRevise,
    ScheduleSeriesRead,
)
from app.modules.operations.schemas import (
    OperationCreate,
    OperationPage,
    OperationRead,
    OperationUpdate,
)

router = APIRouter(prefix="/api/operations", tags=["operations"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get(
    "/vidrieras/{vidriera_id}/operations",
    response_model=OperationPage,
)
def list_operations(
    vidriera_id: uuid.UUID,
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    operation_type: Annotated[str | None, Query()] = None,
    start: Annotated[date | None, Query(alias="from")] = None,
    end: Annotated[date | None, Query(alias="to")] = None,
    cycle: Annotated[str | None, Query()] = None,
    cursor: Annotated[str | None, Query()] = None,
) -> OperationPage:
    return records.list_operations(
        session,
        vidriera_id,
        limit=limit,
        operation_type=operation_type or None,
        start=start,
        end=end,
        cycle=cycle or None,
        cursor=cursor or None,
    )


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


@router.get(
    "/vidrieras/{vidriera_id}/schedules",
    response_model=list[ScheduleSeriesRead],
)
def list_schedules(
    vidriera_id: uuid.UUID,
    session: DbSession,
) -> list[ScheduleSeriesRead]:
    return schedules.list_schedules(session, vidriera_id)


@router.post(
    "/vidrieras/{vidriera_id}/schedules",
    response_model=ScheduleSeriesRead,
    status_code=201,
)
def create_schedule(
    vidriera_id: uuid.UUID,
    payload: ScheduleCreate,
    session: DbSession,
) -> ScheduleSeriesRead:
    return schedules.create_schedule(session, vidriera_id, payload)


@router.get("/schedules/{series_id}", response_model=ScheduleSeriesRead)
def get_schedule(series_id: uuid.UUID, session: DbSession) -> ScheduleSeriesRead:
    return schedules.get_schedule(session, series_id)


@router.post(
    "/schedules/{series_id}/revisions",
    response_model=ScheduleSeriesRead,
)
def revise_schedule(
    series_id: uuid.UUID,
    payload: ScheduleRevise,
    session: DbSession,
) -> ScheduleSeriesRead:
    return schedules.revise_schedule(session, series_id, payload)


@router.post("/schedules/{series_id}/pause", response_model=ScheduleSeriesRead)
def pause_schedule(
    series_id: uuid.UUID,
    payload: ScheduleEffectiveFrom,
    session: DbSession,
) -> ScheduleSeriesRead:
    return schedules.pause_schedule(session, series_id, payload)


@router.post("/schedules/{series_id}/resume", response_model=ScheduleSeriesRead)
def resume_schedule(
    series_id: uuid.UUID,
    payload: ScheduleEffectiveFrom,
    session: DbSession,
) -> ScheduleSeriesRead:
    return schedules.resume_schedule(session, series_id, payload)


@router.post("/schedules/{series_id}/end", response_model=ScheduleSeriesRead)
def end_schedule(
    series_id: uuid.UUID,
    payload: ScheduleEnd,
    session: DbSession,
) -> ScheduleSeriesRead:
    return schedules.end_schedule(session, series_id, payload)


@router.get(
    "/vidrieras/{vidriera_id}/occurrences",
    response_model=list[OccurrenceRead],
)
def list_occurrences(
    vidriera_id: uuid.UUID,
    session: DbSession,
    start: Annotated[date, Query(alias="from")],
    end: Annotated[date, Query(alias="to")],
    operation_type: Annotated[str | None, Query()] = None,
    status: Annotated[
        Literal["scheduled", "unverified", "confirmed", "not_occurred"] | None,
        Query(),
    ] = None,
) -> list[OccurrenceRead]:
    return schedules.list_occurrences(
        session,
        vidriera_id,
        start,
        end,
        operation_type=operation_type,
        status=status,
    )


@router.post(
    "/vidrieras/{vidriera_id}/occurrences/resolve",
    response_model=ResolveResult,
)
def resolve_occurrence(
    vidriera_id: uuid.UUID,
    payload: OccurrenceResolve,
    session: DbSession,
) -> ResolveResult:
    return resolutions.resolve_one(session, vidriera_id, payload)


@router.post(
    "/vidrieras/{vidriera_id}/occurrences/resolve-batch",
    response_model=list[ResolveResult],
)
def resolve_occurrence_batch(
    vidriera_id: uuid.UUID,
    payload: BatchResolve,
    session: DbSession,
) -> list[ResolveResult]:
    return resolutions.resolve_batch(session, vidriera_id, payload)
