import uuid

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


def _reject_fields(value: object, names: set[str], detail: str) -> object:
    if isinstance(value, dict) and names.intersection(value):
        raise DomainError(409, detail)
    return value
