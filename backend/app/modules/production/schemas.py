import uuid
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
