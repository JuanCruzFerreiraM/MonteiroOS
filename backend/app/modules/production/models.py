import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Quinta(Base):
    __tablename__ = "quintas"
    __table_args__ = (
        UniqueConstraint("code", name="uq_quintas_code"),
        UniqueConstraint("name_key", name="uq_quintas_name"),
        CheckConstraint(
            "code ~ '^[A-Z][A-Z0-9]{1,11}$'",
            name="ck_quintas_code",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(12), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_key: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    vidrieras: Mapped[list["Vidriera"]] = relationship(back_populates="quinta")


class Vidriera(Base):
    __tablename__ = "vidrieras"
    __table_args__ = (
        UniqueConstraint("code", name="uq_vidrieras_code"),
        UniqueConstraint("quinta_id", "number", name="uq_vidrieras_quinta_number"),
        UniqueConstraint("quinta_id", "name_key", name="uq_vidrieras_quinta_name"),
        CheckConstraint("number >= 1", name="ck_vidrieras_number_positive"),
        CheckConstraint(
            "code ~ '^[A-Z][A-Z0-9]{1,11}-V[0-9]+$'"
            " AND substring(code from '-V([0-9]+)$')::integer = number"
            " AND code = split_part(code, '-V', 1) || '-V' || "
            "lpad(number::text, greatest(3, char_length(number::text)), '0')",
            name="ck_vidrieras_code_matches_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    quinta_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("quintas.id", ondelete="RESTRICT"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_key: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    quinta: Mapped[Quinta] = relationship(back_populates="vidrieras")
    canteros: Mapped[list["Cantero"]] = relationship(back_populates="vidriera")


class Cantero(Base):
    __tablename__ = "canteros"
    __table_args__ = (
        UniqueConstraint("vidriera_id", "number", name="uq_canteros_vidriera_number"),
        UniqueConstraint("vidriera_id", "name_key", name="uq_canteros_vidriera_name"),
        CheckConstraint("number >= 1 AND number <= 4", name="ck_canteros_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    vidriera_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("vidrieras.id", ondelete="RESTRICT"),
        nullable=False,
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    vidriera: Mapped[Vidriera] = relationship(back_populates="canteros")
