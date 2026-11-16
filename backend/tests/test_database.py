from sqlalchemy import text

from app.core.database import engine, get_db_session


def test_database_accepts_connection() -> None:
    with engine.connect() as connection:
        value = connection.execute(text("SELECT 1")).scalar_one()

    assert value == 1


def test_session_can_query_database() -> None:
    generator = get_db_session()
    session = next(generator)
    try:
        value = session.execute(text("SELECT 1")).scalar_one()
    finally:
        generator.close()

    assert value == 1
