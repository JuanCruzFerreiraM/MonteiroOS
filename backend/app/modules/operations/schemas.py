import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.operations.catalog import require_operation_type
from app.modules.operations.clock import ensure_aware
from app.modules.production.rules import DomainError


class OperationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_type: str
    occurred_at: datetime
    cycle_id: uuid.UUID | None = None
    notes: str | None = None
    interval_start: datetime | None = None
    interval_end: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_create(cls, value: object) -> object:
        body = _object(value)
        unknown = set(body) - {
            "operation_type",
            "occurred_at",
            "cycle_id",
            "notes",
            "interval_start",
            "interval_end",
        }
        if unknown:
            raise DomainError(
                422,
                "Una operación registra tipo, momento, ciclo opcional, notas "
                "y, para iluminación o nylon, un intervalo real.",
            )
        parsed = dict(body)
        parsed["operation_type"] = require_operation_type(body.get("operation_type"))
        parsed["occurred_at"] = _required_timestamp(
            body.get("occurred_at"),
            "fecha y hora",
        )
        parsed["cycle_id"] = _optional_uuid(body.get("cycle_id"), "ciclo")
        _notes(body.get("notes"))
        parsed["interval_start"] = _optional_timestamp(
            body.get("interval_start"),
            "inicio real",
        )
        parsed["interval_end"] = _optional_timestamp(
            body.get("interval_end"),
            "fin real",
        )
        return parsed


class OperationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_type: str | None = None
    occurred_at: datetime | None = None
    cycle_id: uuid.UUID | None = None
    notes: str | None = None
    interval_start: datetime | None = None
    interval_end: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_update(cls, value: object) -> object:
        body = _object(value)
        if {"id", "vidriera_id", "origin", "resolution_id"}.intersection(body):
            raise DomainError(
                409,
                "La vidriera y el origen de una operación no se pueden cambiar.",
            )
        allowed = {
            "operation_type",
            "occurred_at",
            "cycle_id",
            "notes",
            "interval_start",
            "interval_end",
        }
        if set(body) - allowed:
            raise DomainError(
                422,
                "La corrección solo admite tipo, momento, ciclo y notas.",
            )
        parsed = dict(body)
        if "operation_type" in body:
            parsed["operation_type"] = require_operation_type(
                body.get("operation_type"),
            )
        if "occurred_at" in body:
            parsed["occurred_at"] = _required_timestamp(
                body.get("occurred_at"),
                "fecha y hora",
            )
        if "cycle_id" in body:
            parsed["cycle_id"] = _optional_uuid(body.get("cycle_id"), "ciclo")
        if "notes" in body:
            _notes(body.get("notes"))
        if "interval_start" in body:
            parsed["interval_start"] = _optional_timestamp(
                body.get("interval_start"),
                "inicio real",
            )
        if "interval_end" in body:
            parsed["interval_end"] = _optional_timestamp(
                body.get("interval_end"),
                "fin real",
            )
        return parsed


class OperationRead(BaseModel):
    id: uuid.UUID
    vidriera_id: uuid.UUID
    operation_type: str
    operation_label: str
    occurred_at: datetime
    cycle_id: uuid.UUID | None
    notes: str | None
    recorded_at: datetime
    updated_at: datetime
    origin: Literal["manual", "scheduled"]
    interval_start: datetime | None
    interval_end: datetime | None
    timing_basis: Literal["operator_entered", "assumed_from_schedule"] | None


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DomainError(422, "El cuerpo de la operación no es válido.")
    return value


def _required_timestamp(value: object, label: str) -> datetime:
    if value in (None, ""):
        raise DomainError(422, f"La {label} es obligatoria.")
    return _timestamp(value, label)


def _optional_timestamp(value: object, label: str) -> datetime | None:
    if value in (None, ""):
        return None
    return _timestamp(value, label)


def _timestamp(value: object, label: str) -> datetime:
    if isinstance(value, datetime):
        return ensure_aware(value, label)
    if not isinstance(value, str):
        raise DomainError(
            422,
            f"La {label} debe ser una fecha y hora con zona horaria.",
        )
    raw = value.strip()
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        raise DomainError(
            422,
            f"La {label} debe ser una fecha y hora con zona horaria.",
        ) from None
    return ensure_aware(parsed, label)


def _optional_uuid(value: object, label: str) -> uuid.UUID | None:
    if value in (None, ""):
        return None
    if isinstance(value, uuid.UUID):
        return value
    if not isinstance(value, str):
        raise DomainError(422, f"El {label} no es válido.")
    try:
        return uuid.UUID(value)
    except ValueError:
        raise DomainError(422, f"El {label} no es válido.") from None


def _notes(value: object) -> None:
    if value is not None and not isinstance(value, str):
        raise DomainError(422, "Las notas deben ser texto.")
