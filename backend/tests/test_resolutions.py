import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import get_db_session
from app.main import create_app
from app.modules.operations.resolution_schemas import OccurrenceResolve
from app.modules.operations.resolutions import resolve_one
from app.modules.production.rules import DomainError
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


@pytest.fixture(autouse=True)
def clean_tables(engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE quintas CASCADE"))


@pytest.fixture
def client(engine, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ACCESS_SECRET", "")
    get_settings.cache_clear()
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


def _vidriera(client: TestClient) -> dict:
    quinta = client.post(
        "/api/production/quintas",
        json={"code": "VE", "name": "Villa"},
    )
    assert quinta.status_code == 201
    created = client.post(
        f"/api/production/quintas/{quinta.json()['id']}/vidrieras",
        json={"code": "VE-V001", "name": "Norte"},
    )
    assert created.status_code == 201
    return created.json()


def _lighting(client: TestClient, vidriera_id: str) -> dict:
    created = client.post(
        f"/api/operations/vidrieras/{vidriera_id}/schedules",
        json={
            "operation_type": "artificial_lighting",
            "effective_start": "2024-06-01",
            "effective_end": "2024-06-05",
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "22:00",
            "end_time": "02:00",
        },
    )
    assert created.status_code == 201
    return created.json()


def test_confirms_one_occurrence_without_assuming_the_cycle(client: TestClient) -> None:
    vidriera = _vidriera(client)
    cycle = client.post(
        f"/api/production/vidrieras/{vidriera['id']}/cycles",
        json={"start_date": "2024-06-01"},
    )
    assert cycle.status_code == 201
    series = _lighting(client, vidriera["id"])["series_id"]
    resolved = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve",
        json={
            "series_id": series,
            "occurrence_date": "2024-06-01",
            "outcome": "confirmed",
            "timing_basis": "assumed_from_schedule",
        },
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["status"] == "confirmed"
    operation = client.get(f"/api/operations/operations/{body['operation_id']}")
    assert operation.status_code == 200
    saved = operation.json()
    assert saved["origin"] == "scheduled"
    assert saved["cycle_id"] is None
    assert saved["timing_basis"] == "assumed_from_schedule"
    assert saved["resolution_id"] == body["resolution_id"]
    assert saved["interval_start"] == "2024-06-02T01:00:00Z"
    assert saved["interval_end"] == "2024-06-02T05:00:00Z"

    repeated = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve",
        json={
            "series_id": series,
            "occurrence_date": "2024-06-01",
            "outcome": "confirmed",
        },
    )
    assert repeated.status_code == 200
    assert repeated.json()["status"] == "unchanged"
    listed = client.get(f"/api/operations/vidrieras/{vidriera['id']}/operations")
    assert len(listed.json()) == 1

    opened = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences",
        params={"from": "2024-06-01", "to": "2024-06-01"},
    )
    assert opened.json()[0]["status"] == "confirmed"
    assert opened.json()[0]["suggested_cycle_id"] == cycle.json()["id"]
    assert opened.json()[0]["cycle_id"] is None
    assert opened.json()[0]["confirmation_method"] == "manual"


def test_batch_reports_conflicts_without_duplicating_successes(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    series = _lighting(client, vidriera["id"])["series_id"]
    first = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve-batch",
        json={
            "items": [
                {
                    "series_id": series,
                    "occurrence_date": "2024-06-01",
                    "outcome": "confirmed",
                    "timing_basis": "assumed_from_schedule",
                },
                {
                    "series_id": series,
                    "occurrence_date": "2024-06-02",
                    "outcome": "not_occurred",
                },
                {
                    "series_id": series,
                    "occurrence_date": "2024-06-03",
                    "outcome": "confirmed",
                    "timing_basis": "assumed_from_schedule",
                },
            ]
        },
    )
    assert first.status_code == 200
    assert [item["status"] for item in first.json()] == [
        "confirmed",
        "not_occurred",
        "confirmed",
    ]
    operations = client.get(f"/api/operations/vidrieras/{vidriera['id']}/operations")
    assert len(operations.json()) == 2
    second = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve-batch",
        json={
            "items": [
                {
                    "series_id": series,
                    "occurrence_date": "2024-06-02",
                    "outcome": "confirmed",
                    "timing_basis": "assumed_from_schedule",
                },
                {
                    "series_id": series,
                    "occurrence_date": "2024-06-04",
                    "outcome": "not_occurred",
                },
            ]
        },
    )
    assert second.status_code == 200
    assert [item["status"] for item in second.json()] == ["conflict", "not_occurred"]
    operations = client.get(f"/api/operations/vidrieras/{vidriera['id']}/operations")
    assert len(operations.json()) == 2
    missed = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences",
        params={"from": "2024-06-02", "to": "2024-06-02", "status": "not_occurred"},
    )
    assert missed.json()[0]["operation_id"] is None
    assert missed.json()[0]["actual_start"] is None


def test_corrects_actual_times_without_changing_the_expected_interval(
    client: TestClient,
    engine,
) -> None:
    vidriera = _vidriera(client)
    created = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/schedules",
        json={
            "operation_type": "black_nylon",
            "effective_start": "2024-06-01",
            "effective_end": "2024-06-03",
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "18:00",
            "end_time": "08:00",
        },
    )
    assert created.status_code == 201
    series = created.json()["series_id"]
    resolved = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve",
        json={
            "series_id": series,
            "occurrence_date": "2024-06-01",
            "outcome": "confirmed",
            "timing_basis": "operator_entered",
            "actual_start": "2024-06-01T18:30:00-03:00",
            "actual_end": "2024-06-02T07:45:00-03:00",
        },
    )
    assert resolved.status_code == 200
    operation_id = resolved.json()["operation_id"]
    corrected = client.patch(
        f"/api/operations/operations/{operation_id}",
        json={
            "interval_start": "2024-06-01T18:40:00-03:00",
            "interval_end": "2024-06-02T07:30:00-03:00",
        },
    )
    assert corrected.status_code == 200
    assert corrected.json()["timing_basis"] == "operator_entered"
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE recurring_operation_schedules "
                "SET start_time = '17:00:00' WHERE series_id = :series"
            ),
            {"series": uuid.UUID(series)},
        )
    occurrence = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences",
        params={"from": "2024-06-01", "to": "2024-06-01"},
    )
    saved = occurrence.json()[0]
    assert saved["expected_start"] == "2024-06-01T21:00:00Z"
    assert saved["expected_end"] == "2024-06-02T11:00:00Z"
    assert saved["actual_start"] == "2024-06-01T21:40:00Z"
    assert saved["actual_end"] == "2024-06-02T10:30:00Z"
    blocked = client.post(
        f"/api/operations/schedules/{series}/revisions",
        json={
            "effective_from": "2024-06-01",
            "effective_end": "2024-06-03",
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "19:00",
            "end_time": "07:00",
        },
    )
    assert blocked.status_code == 422


def test_rejects_a_future_occurrence_and_keeps_manual_records(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    schedule = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/schedules",
        json={
            "operation_type": "artificial_lighting",
            "effective_start": "2026-12-01",
            "effective_end": "2026-12-20",
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "22:00",
            "end_time": "02:00",
        },
    )
    assert schedule.status_code == 201
    early = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve",
        json={
            "series_id": schedule.json()["series_id"],
            "occurrence_date": "2026-12-01",
            "outcome": "confirmed",
        },
    )
    assert early.status_code == 422
    assert "adelantado" in early.json()["detail"]
    manual = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/operations",
        json={
            "operation_type": "artificial_lighting",
            "occurred_at": "2024-06-01T23:00:00-03:00",
            "interval_start": "2024-06-01T23:00:00-03:00",
            "interval_end": "2024-06-02T01:00:00-03:00",
        },
    )
    assert manual.status_code == 201
    assert manual.json()["origin"] == "manual"
    assert manual.json()["resolution_id"] is None


def test_concurrent_confirmations_leave_a_single_operation(client, engine) -> None:
    vidriera = _vidriera(client)
    series = _lighting(client, vidriera["id"])["series_id"]
    vidriera_id = uuid.UUID(vidriera["id"])
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def attempt(outcome: str) -> str:
        body: dict[str, str] = {
            "series_id": series,
            "occurrence_date": "2024-06-01",
            "outcome": outcome,
        }
        if outcome == "confirmed":
            body["timing_basis"] = "assumed_from_schedule"
        item = OccurrenceResolve.model_validate(body)
        session = factory()
        try:
            result = resolve_one(session, vidriera_id, item)
        except DomainError as error:
            return f"error:{error.status_code}"
        else:
            return result.status
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, ("confirmed", "not_occurred")))
    assert outcomes.count("error:409") == 1
    assert set(outcomes) <= {"confirmed", "not_occurred", "error:409"}
    with engine.connect() as connection:
        stored = connection.scalar(text("SELECT count(*) FROM occurrence_resolutions"))
    assert stored == 1


def test_downgrade_removes_resolutions_and_keeps_manual_operations() -> None:
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    config = _alembic_config()
    try:
        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.begin() as connection:
            quinta_id = uuid.uuid4()
            vidriera_id = uuid.uuid4()
            operation_id = uuid.uuid4()
            moment = "2024-06-01T15:00:00+00:00"
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
                {"id": uuid.uuid4(), "vidriera_id": vidriera_id},
            )
            connection.execute(
                text(
                    "INSERT INTO operations "
                    "(id, vidriera_id, operation_type, occurred_at, recorded_at, "
                    "updated_at, origin) "
                    "VALUES (:id, :vidriera_id, 'irrigation', :moment, :moment, "
                    ":moment, 'manual')"
                ),
                {
                    "id": operation_id,
                    "vidriera_id": vidriera_id,
                    "moment": moment,
                },
            )
        connected.dispose()
        command.downgrade(config, "0005_recurring_schedules")
        connected = create_engine(url)
        with connected.connect() as connection:
            resolutions = connection.scalar(
                text("SELECT to_regclass('public.occurrence_resolutions')")
            )
            kept = connection.scalar(
                text("SELECT origin FROM operations WHERE id = :id"),
                {"id": operation_id},
            )
            cycle = connection.scalar(text("SELECT start_date FROM cultivation_cycles"))
        connected.dispose()
        assert resolutions is None
        assert kept == "manual"
        assert str(cycle) == "2024-05-01"
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)
