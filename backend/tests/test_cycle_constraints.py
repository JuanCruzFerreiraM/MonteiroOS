import uuid
from datetime import date

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from tests.db_isolation import (
    create_isolated_database,
    drop_isolated_database,
    restore_alembic_url,
    use_alembic_url,
)

BACKEND_ROOT = __file__.rsplit("/tests/", 1)[0]


def _alembic_config() -> Config:
    return Config(f"{BACKEND_ROOT}/alembic.ini")


@pytest.fixture(scope="module")
def engine():
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    try:
        command.upgrade(_alembic_config(), "head")
        connected = create_engine(url, pool_pre_ping=True)
        yield connected
        connected.dispose()
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)


@pytest.fixture
def vidriera(engine) -> uuid.UUID:
    quinta_id = uuid.uuid4()
    vidriera_id = uuid.uuid4()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO quintas (id, code, name, name_key, active) "
                "VALUES (:id, 'VE', 'Villa', 'villa', true)"
            ),
            {"id": quinta_id},
        )
        connection.execute(
            text(
                "INSERT INTO vidrieras "
                "(id, quinta_id, code, number, name, name_key, active) "
                "VALUES (:id, :quinta_id, 'VE-V001', 1, 'Norte', 'norte', true)"
            ),
            {"id": vidriera_id, "quinta_id": quinta_id},
        )
    yield vidriera_id
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE quintas CASCADE"))


def _insert_cycle(
    connection,
    vidriera_id: uuid.UUID,
    start: date,
    end: date | None,
) -> uuid.UUID:
    cycle_id = uuid.uuid4()
    connection.execute(
        text(
            "INSERT INTO cultivation_cycles "
            "(id, vidriera_id, start_date, end_date) "
            "VALUES (:id, :vidriera_id, :start_date, :end_date)"
        ),
        {
            "id": cycle_id,
            "vidriera_id": vidriera_id,
            "start_date": start,
            "end_date": end,
        },
    )
    return cycle_id


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(getattr(error, "orig", None), "diag", None)
    return getattr(diagnostic, "constraint_name", None)


def test_cycle_table_derives_status_and_installs_btree_gist(engine) -> None:
    with engine.connect() as connection:
        columns = set(
            connection.scalars(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' "
                    "AND table_name = 'cultivation_cycles'"
                )
            )
        )
        extension = connection.scalar(
            text("SELECT extname FROM pg_extension WHERE extname = 'btree_gist'")
        )
        exclusion = connection.scalar(
            text(
                "SELECT contype FROM pg_constraint "
                "WHERE conname = 'ex_cultivation_cycles_no_overlap'"
            )
        )
        partial = connection.scalar(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE indexname = 'uq_cultivation_cycles_one_active'"
            )
        )

    assert columns == {"id", "vidriera_id", "start_date", "end_date", "notes"}
    assert extension == "btree_gist"
    assert exclusion == "x"
    assert partial is not None
    assert "UNIQUE" in partial
    assert "end_date IS NULL" in partial


def test_one_active_cycle_per_vidriera_and_the_rejected_row_is_rolled_back(
    engine, vidriera: uuid.UUID
) -> None:
    with engine.begin() as connection:
        _insert_cycle(connection, vidriera, date(2024, 1, 1), None)

    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            _insert_cycle(connection, vidriera, date(2024, 6, 1), None)

    with engine.connect() as connection:
        remaining = connection.scalar(
            text(
                "SELECT count(*) FROM cultivation_cycles "
                "WHERE vidriera_id = :vidriera_id"
            ),
            {"vidriera_id": vidriera},
        )

    assert _constraint_name(error.value) == "uq_cultivation_cycles_one_active"
    assert remaining == 1


def test_inclusive_overlap_is_rejected_and_the_next_day_is_accepted(
    engine, vidriera: uuid.UUID
) -> None:
    with engine.begin() as connection:
        _insert_cycle(connection, vidriera, date(2024, 1, 1), date(2024, 3, 1))

    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            _insert_cycle(connection, vidriera, date(2024, 3, 1), date(2024, 4, 1))

    with engine.begin() as connection:
        _insert_cycle(connection, vidriera, date(2024, 3, 2), date(2024, 4, 1))
        stored = connection.scalar(
            text(
                "SELECT count(*) FROM cultivation_cycles "
                "WHERE vidriera_id = :vidriera_id"
            ),
            {"vidriera_id": vidriera},
        )

    assert _constraint_name(error.value) == "ex_cultivation_cycles_no_overlap"
    assert stored == 2


def test_an_open_cycle_blocks_any_later_period(engine, vidriera: uuid.UUID) -> None:
    with engine.begin() as connection:
        _insert_cycle(connection, vidriera, date(2024, 1, 1), None)

    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            _insert_cycle(connection, vidriera, date(2024, 6, 1), date(2024, 8, 1))

    assert _constraint_name(error.value) == "ex_cultivation_cycles_no_overlap"


def test_end_date_cannot_precede_planting(engine, vidriera: uuid.UUID) -> None:
    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            _insert_cycle(connection, vidriera, date(2024, 3, 2), date(2024, 3, 1))

    assert _constraint_name(error.value) == "ck_cultivation_cycles_end_not_before_start"


def test_a_cycle_requires_an_existing_vidriera(engine) -> None:
    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            _insert_cycle(connection, uuid.uuid4(), date(2024, 1, 1), None)

    assert _constraint_name(error.value) == "fk_cultivation_cycles_vidriera_id"


def test_two_vidrieras_can_hold_active_cycles_on_the_same_dates(
    engine, vidriera: uuid.UUID
) -> None:
    other_quinta = uuid.uuid4()
    other_vidriera = uuid.uuid4()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO quintas (id, code, name, name_key, active) "
                "VALUES (:id, 'AS', 'Segui', 'segui', true)"
            ),
            {"id": other_quinta},
        )
        connection.execute(
            text(
                "INSERT INTO vidrieras "
                "(id, quinta_id, code, number, name, name_key, active) "
                "VALUES (:id, :quinta_id, 'AS-V001', 1, 'Sur', 'sur', true)"
            ),
            {"id": other_vidriera, "quinta_id": other_quinta},
        )
        _insert_cycle(connection, vidriera, date(2024, 1, 1), None)
        _insert_cycle(connection, other_vidriera, date(2024, 1, 1), None)
        stored = connection.scalar(text("SELECT count(*) FROM cultivation_cycles"))

    assert stored == 2


def test_upgrade_from_boundaries_keeps_existing_rows_and_downgrade_drops_cycles() -> (
    None
):
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    config = _alembic_config()
    quinta_id = uuid.uuid4()
    vidriera_id = uuid.uuid4()
    boundary = '{"type":"Polygon","coordinates":[[[1,2],[3,4],[5,6],[1,2]]]}'
    try:
        command.upgrade(config, "0002_production_boundaries")
        connected = create_engine(url)
        with connected.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO quintas "
                    "(id, code, name, name_key, active, boundary) "
                    "VALUES (:id, 'VE', 'Villa', 'villa', true, "
                    "CAST(:boundary AS jsonb))"
                ),
                {"id": quinta_id, "boundary": boundary},
            )
            connection.execute(
                text(
                    "INSERT INTO vidrieras "
                    "(id, quinta_id, code, number, name, name_key, active, "
                    "boundary) "
                    "VALUES (:id, :quinta_id, 'VE-V001', 1, 'Norte', 'norte', "
                    "true, CAST(:boundary AS jsonb))"
                ),
                {
                    "id": vidriera_id,
                    "quinta_id": quinta_id,
                    "boundary": boundary,
                },
            )
            cantero_id = uuid.uuid4()
            connection.execute(
                text(
                    "INSERT INTO canteros (id, vidriera_id, number, active) "
                    "VALUES (:id, :vidriera_id, 1, true)"
                ),
                {"id": cantero_id, "vidriera_id": vidriera_id},
            )
        connected.dispose()

        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.connect() as connection:
            quinta_boundary = connection.scalar(
                text("SELECT boundary::text FROM quintas WHERE id = :id"),
                {"id": quinta_id},
            )
            vidriera_code = connection.scalar(
                text("SELECT code FROM vidrieras WHERE id = :id"),
                {"id": vidriera_id},
            )
            cantero_number = connection.scalar(
                text("SELECT number FROM canteros WHERE id = :id"),
                {"id": cantero_id},
            )
            cycle_table = connection.scalar(
                text("SELECT to_regclass('public.cultivation_cycles')")
            )
        connected.dispose()
        assert "Polygon" in str(quinta_boundary)
        assert vidriera_code == "VE-V001"
        assert cantero_number == 1
        assert cycle_table == "cultivation_cycles"

        command.downgrade(config, "0002_production_boundaries")
        connected = create_engine(url)
        with connected.connect() as connection:
            cycle_table = connection.scalar(
                text("SELECT to_regclass('public.cultivation_cycles')")
            )
            vidriera_code = connection.scalar(
                text("SELECT code FROM vidrieras WHERE id = :id"),
                {"id": vidriera_id},
            )
            still_there = connection.scalar(
                text("SELECT boundary::text FROM quintas WHERE id = :id"),
                {"id": quinta_id},
            )
        connected.dispose()
        assert cycle_table is None
        assert vidriera_code == "VE-V001"
        assert "Polygon" in str(still_there)
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)
