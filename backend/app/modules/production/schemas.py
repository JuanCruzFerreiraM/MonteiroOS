import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.production.rules import DomainError


class QuintaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    notes: str | None = None


class QuintaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    notes: str | None = None
    active: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_identity_fields(cls, value: object) -> object:
        return _reject_fields(
            value,
            {"id", "code"},
            "El código de una quinta no se puede cambiar.",
        )


class QuintaRead(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    notes: str | None
    active: bool


class VidrieraCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    notes: str | None = None


class VidrieraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    notes: str | None = None
    active: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_identity_fields(cls, value: object) -> object:
        return _reject_fields(
            value,
            {"id", "code", "quinta_id", "number"},
            "El código y la quinta de una vidriera no se pueden cambiar.",
        )


class CanteroRead(BaseModel):
    id: uuid.UUID
    number: int
    display_code: str
    name: str | None
    active: bool


class VidrieraRead(BaseModel):
    id: uuid.UUID
    quinta_id: uuid.UUID
    code: str
    name: str
    notes: str | None
    active: bool


class VidrieraDetail(VidrieraRead):
    quinta_code: str
    quinta_name: str
    canteros: list[CanteroRead]


class CanteroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    active: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_identity_fields(cls, value: object) -> object:
        return _reject_fields(
            value,
            {"id", "number", "vidriera_id", "display_code"},
            "El número y la vidriera de un cantero no se pueden cambiar.",
        )


class NextVidrieraCode(BaseModel):
    code: str
    number: int


class BoundaryWarningRead(BaseModel):
    code: str
    message: str
    vidriera_id: uuid.UUID | None = None
    vidriera_code: str | None = None


class BoundaryRead(BaseModel):
    """An existing production record. `geometry` is null when it has no boundary."""

    id: uuid.UUID
    geometry: dict[str, Any] | None
    warnings: list[BoundaryWarningRead]


class BoundaryWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    geometry: dict[str, Any]
    mode: Literal["replace", "attach"] = "replace"

    @model_validator(mode="before")
    @classmethod
    def require_polygon_body(cls, value: object) -> object:
        if not isinstance(value, dict):
            raise DomainError(422, "El cuerpo debe incluir la geometría del polígono.")
        unknown = set(value) - {"geometry", "mode"}
        if unknown:
            raise DomainError(422, "El cuerpo solo admite geometry y mode.")
        if "geometry" not in value:
            raise DomainError(422, "Falta la geometría del polígono.")
        if not isinstance(value.get("geometry"), dict):
            raise DomainError(
                422,
                "La geometría debe ser un objeto GeoJSON Polygon.",
            )
        if "mode" in value and value["mode"] not in {"replace", "attach"}:
            raise DomainError(422, "El modo debe ser replace o attach.")
        return value


class MapVidrieraRead(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    active: bool
    geometry: dict[str, Any] | None
    warnings: list[BoundaryWarningRead]


class QuintaMapRead(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    active: bool
    geometry: dict[str, Any] | None
    vidrieras: list[MapVidrieraRead]


def _reject_fields(value: object, names: set[str], detail: str) -> object:
    if isinstance(value, dict) and names.intersection(value):
        raise DomainError(409, detail)
    return value


def _parse_cycle_date(value: object, label: str) -> date:
    if isinstance(value, datetime):
        raise DomainError(422, f"La {label} debe ser una fecha válida (AAAA-MM-DD).")
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise DomainError(422, f"La {label} es obligatoria.")
    raw = value.strip()
    if len(raw) != 10:
        raise DomainError(422, f"La {label} debe ser una fecha válida (AAAA-MM-DD).")
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        raise DomainError(
            422,
            f"La {label} debe ser una fecha válida (AAAA-MM-DD).",
        ) from None
    if isinstance(parsed, datetime):
        raise DomainError(422, f"La {label} debe ser una fecha válida (AAAA-MM-DD).")
    return parsed


def _require_object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DomainError(422, "El cuerpo del ciclo no es válido.")
    return value


class CycleStart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_date: date
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_planting(cls, value: object) -> object:
        body = _require_object(value)
        unknown = set(body) - {"start_date", "notes"}
        if unknown:
            raise DomainError(
                422,
                "Un ciclo solo registra la fecha de plantación y notas. "
                "La variedad, el color y el tamaño se cargan después.",
            )
        if "start_date" not in body or body["start_date"] in (None, ""):
            raise DomainError(422, "La fecha de plantación es obligatoria.")
        if (
            "notes" in body
            and body["notes"] is not None
            and not isinstance(body["notes"], str)
        ):
            raise DomainError(422, "Las notas deben ser texto.")
        parsed = dict(body)
        parsed["start_date"] = _parse_cycle_date(
            body["start_date"],
            "fecha de plantación",
        )
        return parsed


class CycleFinalize(BaseModel):
    model_config = ConfigDict(extra="forbid")

    end_date: date

    @model_validator(mode="before")
    @classmethod
    def parse_closing(cls, value: object) -> object:
        body = _require_object(value)
        if set(body) - {"end_date"}:
            raise DomainError(422, "La finalización solo admite la fecha de cierre.")
        if "end_date" not in body or body["end_date"] in (None, ""):
            raise DomainError(422, "La fecha de cierre es obligatoria.")
        return {
            "end_date": _parse_cycle_date(body["end_date"], "fecha de cierre"),
        }


class CycleCorrection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_correction(cls, value: object) -> object:
        body = _require_object(value)
        if {"id", "vidriera_id", "status"}.intersection(body):
            raise DomainError(
                409,
                "El identificador y la vidriera de un ciclo no se pueden cambiar, "
                "y el estado solo cambia al finalizarlo.",
            )
        if set(body) - {"start_date", "end_date", "notes"}:
            raise DomainError(422, "Una corrección solo admite fechas y notas.")
        if (
            "notes" in body
            and body["notes"] is not None
            and not isinstance(body["notes"], str)
        ):
            raise DomainError(422, "Las notas deben ser texto.")
        parsed = dict(body)
        if "start_date" in body:
            if body["start_date"] in (None, ""):
                raise DomainError(422, "La fecha de plantación es obligatoria.")
            parsed["start_date"] = _parse_cycle_date(
                body["start_date"],
                "fecha de plantación",
            )
        if "end_date" in body and body["end_date"] not in (None, ""):
            parsed["end_date"] = _parse_cycle_date(body["end_date"], "fecha de cierre")
        if "end_date" in body and body["end_date"] == "":
            raise DomainError(422, "La fecha de cierre debe ser una fecha válida.")
        return parsed


class CycleRead(BaseModel):
    id: uuid.UUID
    vidriera_id: uuid.UUID
    start_date: date
    end_date: date | None
    status: Literal["active", "finalized"]
    notes: str | None


class CycleCollection(BaseModel):
    active: CycleRead | None
    history: list[CycleRead]
