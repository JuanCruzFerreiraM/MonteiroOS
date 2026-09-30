from sqlalchemy import text

from app.core.database import engine


def test_database_accepts_connection() -> None:
    with engine.connect() as connection:
        value = connection.execute(text("SELECT 1")).scalar_one()

    assert value == 1
