import uuid
from datetime import UTC, datetime, timedelta

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.database import get_db_session
from app.main import create_app
from tests.db_isolation import (
    create_isolated_database,
    drop_isolated_database,
    restore_alembic_url,
    use_alembic_url,
)

BACKEND_ROOT = __file__.rsplit("/tests/", 1)[0]
PAST = "2024-06-01T15:00:00-03:00"


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


@pytest.fixture(autouse=True)
def clean_tables(engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE quintas CASCADE"))


@pytest.fixture
def client(engine, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ACCESS_SECRET", "")
    get_settings.cache_clear()
    from sqlalchemy.orm import sessionmaker

    sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_session():
        session = sessions()
        try:
            yield session
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[get_db_session] = override_session
    try:
        with TestClient(application) as test_client:
            yield test_client
    finally:
        get_settings.cache_clear()


def _vidriera(client: TestClient, code: str = "VE", name: str = "Villa Elisa") -> dict:
    quinta = client.post(
        "/api/production/quintas",
        json={"code": code, "name": name},
    )
    assert quinta.status_code == 201
    created = client.post(
        f"/api/production/quintas/{quinta.json()['id']}/vidrieras",
        json={"code": f"{code}-V001", "name": "Norte"},
    )
    assert created.status_code == 201
    return created.json()


def _cycle(
    client: TestClient,
    vidriera_id: str,
    start: str,
    end: str | None = None,
) -> dict:
    created = client.post(
        f"/api/production/vidrieras/{vidriera_id}/cycles",
        json={"start_date": start},
    )
    assert created.status_code == 201
    if end is not None:
        closed = client.post(
            f"/api/production/cycles/{created.json()['id']}/finalize",
            json={"end_date": end},
        )
        assert closed.status_code == 200
        return closed.json()
    return created.json()


def _operation(client: TestClient, vidriera_id: str, **extra):
    body = {"operation_type": "irrigation", "occurred_at": PAST}
    body.update(extra)
    return client.post(f"/api/operations/vidrieras/{vidriera_id}/operations", json=body)


def test_records_a_manual_operation_without_a_cycle_or_beds(client: TestClient) -> None:
    vidriera = _vidriera(client)
    active = _cycle(client, vidriera["id"], "2024-05-01")
    created = _operation(client, vidriera["id"], notes="  riego de la mañana  ")

    assert created.status_code == 201
    body = created.json()
    assert body["vidriera_id"] == vidriera["id"]
    assert body["operation_type"] == "irrigation"
    assert body["operation_label"] == "Riego"
    assert body["cycle_id"] is None
    assert body["origin"] == "manual"
    assert body["notes"] == "riego de la mañana"
    assert body["interval_start"] is None
    assert "cantero" not in body
    assert uuid.UUID(body["id"])
    listed = client.get(f"/api/operations/vidrieras/{vidriera['id']}/operations")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [body["id"]]
    assert active["id"] != body["cycle_id"]


def test_two_saves_create_two_operations(client: TestClient) -> None:
    vidriera = _vidriera(client)
    first = _operation(client, vidriera["id"])
    second = _operation(client, vidriera["id"], occurred_at="2024-06-02T09:00:00-03:00")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    listed = client.get(f"/api/operations/vidrieras/{vidriera['id']}/operations").json()
    assert [item["id"] for item in listed] == [second.json()["id"], first.json()["id"]]


def test_accepts_an_explicit_finalized_cycle_and_rejects_another_vidriera(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    other = _vidriera(client, "AS", "Arturo Seguí")
    finalized = _cycle(client, vidriera["id"], "2024-01-01", "2024-03-01")
    other_cycle = _cycle(client, other["id"], "2024-01-01")

    accepted = _operation(client, vidriera["id"], cycle_id=finalized["id"])
    rejected = _operation(client, vidriera["id"], cycle_id=other_cycle["id"])
    missing = _operation(client, vidriera["id"], cycle_id=str(uuid.uuid4()))

    assert accepted.status_code == 201
    assert accepted.json()["cycle_id"] == finalized["id"]
    assert rejected.status_code == 422
    assert "vidriera" in rejected.json()["detail"]
    assert missing.status_code == 422


def test_rejects_a_future_timestamp_and_a_naive_one(client: TestClient) -> None:
    vidriera = _vidriera(client)
    future = (datetime.now(UTC) + timedelta(hours=2)).isoformat()
    soon = (datetime.now(UTC) + timedelta(minutes=2)).isoformat()

    rejected = _operation(client, vidriera["id"], occurred_at=future)
    allowed = _operation(client, vidriera["id"], occurred_at=soon)
    naive = _operation(client, vidriera["id"], occurred_at="2024-06-01T15:00:00")

    assert rejected.status_code == 422
    assert "futuro" in rejected.json()["detail"]
    assert allowed.status_code == 201
    assert naive.status_code == 422
    assert "zona horaria" in naive.json()["detail"]


def test_edits_type_time_cycle_and_notes_without_changing_identity(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    other = _vidriera(client, "AS", "Arturo Seguí")
    cycle = _cycle(client, vidriera["id"], "2024-05-01")
    created = _operation(client, vidriera["id"]).json()

    updated = client.patch(
        f"/api/operations/operations/{created['id']}",
        json={
            "operation_type": "observation",
            "occurred_at": "2024-06-03T11:00:00-03:00",
            "cycle_id": cycle["id"],
            "notes": "hoja amarilla",
        },
    )
    ownership = client.patch(
        f"/api/operations/operations/{created['id']}",
        json={"vidriera_id": other["id"]},
    )
    stored = client.get(f"/api/operations/operations/{created['id']}").json()

    assert updated.status_code == 200
    assert updated.json()["id"] == created["id"]
    assert updated.json()["vidriera_id"] == vidriera["id"]
    assert stored["operation_type"] == "observation"
    assert stored["cycle_id"] == cycle["id"]
    assert stored["notes"] == "hoja amarilla"
    assert ownership.status_code == 409


def test_lighting_interval_can_cross_midnight_and_is_rejected_for_irrigation(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    lighting = _operation(
        client,
        vidriera["id"],
        operation_type="artificial_lighting",
        occurred_at="2024-06-01T22:00:00-03:00",
        interval_start="2024-06-01T22:00:00-03:00",
        interval_end="2024-06-02T02:00:00-03:00",
    )
    backwards = _operation(
        client,
        vidriera["id"],
        operation_type="black_nylon",
        interval_start="2024-06-02T08:00:00-03:00",
        interval_end="2024-06-01T18:00:00-03:00",
    )
    irrigation = _operation(
        client,
        vidriera["id"],
        interval_start="2024-06-01T10:00:00-03:00",
        interval_end="2024-06-01T11:00:00-03:00",
    )

    assert lighting.status_code == 201
    assert lighting.json()["timing_basis"] == "operator_entered"
    assert lighting.json()["origin"] == "manual"
    assert backwards.status_code == 422
    assert irrigation.status_code == 422


def test_unknown_operation_and_vidriera(client: TestClient) -> None:
    missing_vidriera = _operation(client, str(uuid.uuid4()))
    missing_operation = client.get(f"/api/operations/operations/{uuid.uuid4()}")
    empty = _vidriera(client)
    listed = client.get(f"/api/operations/vidrieras/{empty['id']}/operations")

    assert missing_vidriera.status_code == 404
    assert missing_operation.status_code == 404
    assert listed.json() == []


def test_database_rejects_an_interval_that_ends_before_it_starts(engine) -> None:
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
    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO operations "
                    "(id, vidriera_id, operation_type, occurred_at, recorded_at, "
                    "updated_at, origin, interval_start, interval_end, timing_basis) "
                    "VALUES (:id, :vidriera_id, 'artificial_lighting', "
                    ":moment, :moment, :moment, 'manual', "
                    ":end_at, :start_at, 'operator_entered')"
                ),
                {
                    "id": uuid.uuid4(),
                    "vidriera_id": vidriera_id,
                    "moment": datetime(2024, 6, 1, 18, tzinfo=UTC),
                    "start_at": datetime(2024, 6, 1, 22, tzinfo=UTC),
                    "end_at": datetime(2024, 6, 2, 2, tzinfo=UTC),
                },
            )
    assert error.value.orig.diag.constraint_name == "ck_operations_interval"


def test_upgrade_preserves_cycles_and_downgrade_drops_operations() -> None:
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    config = _alembic_config()
    quinta_id = uuid.uuid4()
    vidriera_id = uuid.uuid4()
    cycle_id = uuid.uuid4()
    try:
        command.upgrade(config, "0003_cultivation_cycles")
        connected = create_engine(url)
        with connected.begin() as connection:
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
            connection.execute(
                text(
                    "INSERT INTO cultivation_cycles (id, vidriera_id, start_date) "
                    "VALUES (:id, :vidriera_id, '2024-05-01')"
                ),
                {"id": cycle_id, "vidriera_id": vidriera_id},
            )
        connected.dispose()
        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.connect() as connection:
            still = connection.scalar(
                text("SELECT start_date FROM cultivation_cycles WHERE id = :id"),
                {"id": cycle_id},
            )
            table = connection.scalar(text("SELECT to_regclass('public.operations')"))
        connected.dispose()
        assert str(still) == "2024-05-01"
        assert table == "operations"
        command.downgrade(config, "0003_cultivation_cycles")
        connected = create_engine(url)
        with connected.connect() as connection:
            table = connection.scalar(text("SELECT to_regclass('public.operations')"))
            still = connection.scalar(
                text("SELECT code FROM vidrieras WHERE id = :id"),
                {"id": vidriera_id},
            )
        connected.dispose()
        assert table is None
        assert still == "VE-V001"
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)
