import os
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from app.core.config import get_settings

ISOLATED_PREFIX = "monteiro_prod01_"
PROTECTED_DATABASES = {"postgres", "template0", "template1"}


def _admin_url(database: str) -> URL:
    return make_url(get_settings().sqlalchemy_url).set(database=database)


def primary_database_name() -> str:
    name = make_url(get_settings().sqlalchemy_url).database
    if not name:
        raise RuntimeError("the application database name is missing")
    return name


def create_isolated_database() -> tuple[str, str]:
    name = f"{ISOLATED_PREFIX}{uuid.uuid4().hex}"
    _assert_disposable(name)
    admin = create_engine(_admin_url("postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
    finally:
        admin.dispose()
    url = _admin_url(name).render_as_string(hide_password=False)
    return name, url


def drop_isolated_database(name: str) -> None:
    _assert_disposable(name)
    admin = create_engine(_admin_url("postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
    finally:
        admin.dispose()


def _assert_disposable(name: str) -> None:
    if (
        not name.startswith(ISOLATED_PREFIX)
        or name in PROTECTED_DATABASES
        or name == primary_database_name()
    ):
        raise RuntimeError(f"refusing to touch database {name}")


def use_alembic_url(url: str) -> str | None:
    previous = os.environ.get("ALEMBIC_URL")
    os.environ["ALEMBIC_URL"] = url
    return previous


def restore_alembic_url(previous: str | None) -> None:
    if previous is None:
        os.environ.pop("ALEMBIC_URL", None)
    else:
        os.environ["ALEMBIC_URL"] = previous
