import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.operations.schemas import _notes, _optional_timestamp, _optional_uuid
from app.modules.production.rules import DomainError

MAX_BATCH = 31


class OccurrenceResolve(BaseModel):
    model_config = ConfigDict(extra="forbid")

    series_id: uuid.UUID
    occurrence_date: date
    outcome: Literal["confirmed", "not_occurred"]
    cycle_id: uuid.UUID | None = None
    notes: str | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    timing_basis: Literal["assumed_from_schedule", "operator_entered"] | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_item(cls, value: object) -> object:
        body = _object(value)
        allowed = {
            "series_id",
            "occurrence_date",
            "outcome",
            "cycle_id",
            "notes",
            "actual_start",
            "actual_end",
            "timing_basis",
        }
        if set(body) - allowed:
            raise DomainError(
                422,
                "La confirmación admite la ocurrencia, el resultado, el ciclo, "
                "las notas y el horario real.",
            )
        outcome = body.get("outcome")
        if outcome not in {"confirmed", "not_occurred"}:
            raise DomainError(422, "El resultado debe ser confirmada o no realizada.")
        basis = body.get("timing_basis")
        if basis not in {None, "assumed_from_schedule", "operator_entered"}:
            raise DomainError(
                422,
                "El horario real es supuesto o indicado por el operador.",
            )
        _notes(body.get("notes"))
        return {
            "series_id": _required_uuid(body.get("series_id")),
            "occurrence_date": _parse_date(body.get("occurrence_date")),
            "outcome": outcome,
            "cycle_id": _optional_uuid(body.get("cycle_id"), "ciclo"),
            "notes": body.get("notes"),
            "actual_start": _optional_timestamp(
                body.get("actual_start"),
                "inicio real",
            ),
            "actual_end": _optional_timestamp(body.get("actual_end"), "fin real"),
            "timing_basis": basis,
        }


class BatchResolve(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[OccurrenceResolve]

    @model_validator(mode="before")
    @classmethod
    def parse_batch(cls, value: object) -> object:
        body = _object(value)
        if set(body) - {"items"}:
            raise DomainError(422, "El lote solo admite la lista de ocurrencias.")
        items = body.get("items")
        if not isinstance(items, list):
            raise DomainError(422, "La confirmación no incluye ocurrencias.")
        if len(items) > MAX_BATCH:
            raise DomainError(
                422,
                "Se pueden resolver hasta 31 ocurrencias por vez.",
            )
        return body


class ResolveResult(BaseModel):
    series_id: uuid.UUID
    occurrence_date: date
    status: Literal["confirmed", "not_occurred", "unchanged", "conflict", "invalid"]
    message: str | None = None
    operation_id: uuid.UUID | None = None
    resolution_id: uuid.UUID | None = None


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DomainError(422, "El cuerpo de la confirmación no es válido.")
    return value


def _required_uuid(value: object) -> uuid.UUID:
    parsed = _optional_uuid(value, "identificador")
    if parsed is None:
        raise DomainError(422, "Falta la programación de la ocurrencia.")
    return parsed


def _parse_date(value: object) -> date:
    if isinstance(value, datetime):
        raise DomainError(422, "La fecha de la ocurrencia debe ser AAAA-MM-DD.")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or len(value.strip()) != 10:
        raise DomainError(422, "La fecha de la ocurrencia debe ser AAAA-MM-DD.")
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise DomainError(
            422,
            "La fecha de la ocurrencia debe ser AAAA-MM-DD.",
        ) from None
