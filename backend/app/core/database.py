from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base reserved for future domain models."""


engine = create_engine(get_settings().sqlalchemy_url, pool_pre_ping=True)


def check_database_connection() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
