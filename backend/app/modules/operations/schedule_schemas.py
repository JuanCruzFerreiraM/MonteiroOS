import uuid
from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.operations.catalog import require_schedule_type
from app.modules.operations.recurrence import (
    normalize_clock,
    normalize_weekdays,
    require_distinct_times,
    require_period,
)
from app.modules.production.rules import DomainError


class ScheduleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_type: str
    effective_start: date
    effective_end: date
    weekdays: list[int]
    start_time: time
    end_time: time
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_create(cls, value: object) -> object:
        body = _object(value)
        allowed = {
            "operation_type",
            "effective_start",
            "effective_end",
            "weekdays",
            "start_time",
            "end_time",
            "notes",
        }
        if set(body) - allowed:
            raise DomainError(
                422,
                "La programación admite tipo, período, días, horario y notas.",
            )
        start = _parse_date(body.get("effective_start"), "fecha de inicio")
        end = _parse_date(body.get("effective_end"), "fecha de fin")
        require_period(start, end)
        parsed = _clock_and_days(body)
        parsed["operation_type"] = require_schedule_type(body.get("operation_type"))
        parsed["effective_start"] = start
        parsed["effective_end"] = end
        return parsed


class ScheduleRevise(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effective_from: date
    effective_end: date
    weekdays: list[int]
    start_time: time
    end_time: time
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_revise(cls, value: object) -> object:
        body = _object(value)
        allowed = {
            "effective_from",
            "effective_end",
            "weekdays",
            "start_time",
            "end_time",
            "notes",
        }
        if set(body) - allowed:
            raise DomainError(
                422,
                "La revisión cambia el período, los días, el horario y las notas.",
            )
        effective_from = _parse_date(
            body.get("effective_from"),
            "fecha del cambio",
        )
        effective_end = _parse_date(body.get("effective_end"), "fecha de fin")
        require_period(effective_from, effective_end)
        parsed = _clock_and_days(body)
        parsed["effective_from"] = effective_from
        parsed["effective_end"] = effective_end
        return parsed


class ScheduleEffectiveFrom(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effective_from: date

    @model_validator(mode="before")
    @classmethod
    def parse_from(cls, value: object) -> object:
        body = _object(value)
        if set(body) - {"effective_from"}:
            raise DomainError(422, "Indique desde qué fecha rige el cambio.")
        return {
            "effective_from": _parse_date(
                body.get("effective_from"),
                "fecha del cambio",
            )
        }


class ScheduleEnd(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effective_end: date | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_end(cls, value: object) -> object:
        body = _object(value)
        if set(body) - {"effective_end"}:
            raise DomainError(422, "El cierre solo admite la fecha de fin.")
        end = body.get("effective_end")
        if end in (None, ""):
            return {"effective_end": None}
        return {"effective_end": _parse_date(end, "fecha de cierre")}


class ScheduleRevisionRead(BaseModel):
    id: uuid.UUID
    series_id: uuid.UUID
    vidriera_id: uuid.UUID
    operation_type: str
    operation_label: str
    effective_start: date
    effective_end: date
    weekdays: list[int]
    start_time: time
    end_time: time
    notes: str | None
    status: Literal["active", "paused", "ended"]
    generates: bool
    created_at: datetime
    updated_at: datetime


class ScheduleSeriesRead(BaseModel):
    series_id: uuid.UUID
    current: ScheduleRevisionRead
    revisions: list[ScheduleRevisionRead]


class OccurrenceRead(BaseModel):
    series_id: uuid.UUID
    revision_id: uuid.UUID
    vidriera_id: uuid.UUID
    occurrence_date: date
    operation_type: str
    operation_label: str
    status: Literal["scheduled", "unverified", "confirmed", "not_occurred"]
    expected_start: datetime
    expected_end: datetime
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    timing_basis: Literal["operator_entered", "assumed_from_schedule"] | None = None
    confirmation_method: Literal["manual"] | None = None
    suggested_cycle_id: uuid.UUID | None = None
    cycle_id: uuid.UUID | None = None
    operation_id: uuid.UUID | None = None
    notes: str | None = None


def _clock_and_days(body: dict[str, Any]) -> dict[str, Any]:
    start_time = normalize_clock(body.get("start_time"), "hora de inicio")
    end_time = normalize_clock(body.get("end_time"), "hora de fin")
    require_distinct_times(start_time, end_time)
    notes = body.get("notes")
    if notes is not None and not isinstance(notes, str):
        raise DomainError(422, "Las notas deben ser texto.")
    return {
        "weekdays": normalize_weekdays(body.get("weekdays")),
        "start_time": start_time,
        "end_time": end_time,
        "notes": notes,
    }


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DomainError(422, "El cuerpo de la programación no es válido.")
    return value


def _parse_date(value: object, label: str) -> date:
    if isinstance(value, datetime):
        raise DomainError(422, f"La {label} debe ser una fecha válida (AAAA-MM-DD).")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or len(value.strip()) != 10:
        raise DomainError(422, f"La {label} debe ser una fecha válida (AAAA-MM-DD).")
    try:
        parsed = date.fromisoformat(value.strip())
    except ValueError:
        raise DomainError(
            422,
            f"La {label} debe ser una fecha válida (AAAA-MM-DD).",
        ) from None
    return parsed
