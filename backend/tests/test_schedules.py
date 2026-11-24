import uuid
from datetime import time, timedelta

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import get_db_session
from app.main import create_app
from app.modules.operations.clock import APP_TIMEZONE, local_today, utc_now
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


def _vidriera(client: TestClient, code: str = "VE") -> dict:
    quinta = client.post(
        "/api/production/quintas",
        json={"code": code, "name": code},
    )
    assert quinta.status_code == 201
    created = client.post(
        f"/api/production/quintas/{quinta.json()['id']}/vidrieras",
        json={"code": f"{code}-V001", "name": "Norte"},
    )
    assert created.status_code == 201
    return created.json()


def _schedule(client: TestClient, vidriera_id: str, **extra) -> object:
    today = local_today()
    body = {
        "operation_type": "artificial_lighting",
        "effective_start": (today - timedelta(days=2)).isoformat(),
        "effective_end": (today + timedelta(days=10)).isoformat(),
        "weekdays": [1, 2, 3, 4, 5, 6, 7],
        "start_time": "22:00",
        "end_time": "02:00",
        "notes": "temporada",
    }
    body.update(extra)
    return client.post(
        f"/api/operations/vidrieras/{vidriera_id}/schedules",
        json=body,
    )


def _occurrences(client: TestClient, vidriera_id: str, start: str, end: str, **query):
    params = {"from": start, "to": end, **query}
    return client.get(
        f"/api/operations/vidrieras/{vidriera_id}/occurrences",
        params=params,
    )


def test_rejects_invalid_schedule_configurations(client: TestClient) -> None:
    vidriera = _vidriera(client)
    irrigation = _schedule(client, vidriera["id"], operation_type="irrigation")
    assert irrigation.status_code == 422
    assert "programación" in irrigation.json()["detail"]

    empty_days = _schedule(client, vidriera["id"], weekdays=[])
    assert empty_days.status_code == 422
    repeated = _schedule(client, vidriera["id"], weekdays=[1, 1])
    assert repeated.status_code == 422
    backwards = _schedule(
        client,
        vidriera["id"],
        effective_start="2024-06-10",
        effective_end="2024-06-01",
    )
    assert backwards.status_code == 422
    same_time = _schedule(client, vidriera["id"], start_time="22:00", end_time="22:00")
    assert same_time.status_code == 422
    assert "iguales" in same_time.json()["detail"]


def test_expands_daily_and_weekday_schedules_including_overnight(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    cycle = client.post(
        f"/api/production/vidrieras/{vidriera['id']}/cycles",
        json={"start_date": "2024-06-01"},
    )
    assert cycle.status_code == 201
    created = _schedule(
        client,
        vidriera["id"],
        effective_start="2024-06-01",
        effective_end="2024-06-03",
    )
    assert created.status_code == 201
    series = created.json()["series_id"]

    listed = _occurrences(client, vidriera["id"], "2024-06-01", "2024-06-03")
    assert listed.status_code == 200
    body = listed.json()
    assert [item["occurrence_date"] for item in body] == [
        "2024-06-01",
        "2024-06-02",
        "2024-06-03",
    ]
    first = body[0]
    assert first["status"] == "unverified"
    assert first["expected_start"].startswith("2024-06-01T22:00:00")
    assert first["expected_end"].startswith("2024-06-02T02:00:00")
    assert first["suggested_cycle_id"] == cycle.json()["id"]
    assert first["operation_id"] is None
    assert first["actual_start"] is None

    ending_day = _occurrences(client, vidriera["id"], "2024-06-02", "2024-06-02")
    assert [item["occurrence_date"] for item in ending_day.json()] == ["2024-06-02"]

    mondays = _schedule(
        client,
        vidriera["id"],
        operation_type="black_nylon",
        effective_start="2024-06-01",
        effective_end="2024-06-10",
        weekdays=[1],
        start_time="18:00",
        end_time="08:00",
    )
    assert mondays.status_code == 201
    nylon = _occurrences(
        client,
        vidriera["id"],
        "2024-06-01",
        "2024-06-10",
        operation_type="black_nylon",
    )
    assert [item["occurrence_date"] for item in nylon.json()] == [
        "2024-06-03",
        "2024-06-10",
    ]
    assert nylon.json()[0]["expected_end"].startswith("2024-06-04T08:00:00")

    too_long = _occurrences(client, vidriera["id"], "2024-06-01", "2024-08-02")
    assert too_long.status_code == 422
    assert "62" in too_long.json()["detail"]

    operations = client.get(f"/api/operations/vidrieras/{vidriera['id']}/operations")
    assert operations.json() == []
    stored = client.get(f"/api/operations/schedules/{series}")
    assert stored.json()["current"]["start_time"] == "22:00:00"


def test_does_not_overwrite_an_overlapping_schedule(client: TestClient) -> None:
    vidriera = _vidriera(client)
    original = _schedule(
        client,
        vidriera["id"],
        effective_start="2026-12-01",
        effective_end="2026-12-20",
    )
    assert original.status_code == 201
    conflict = _schedule(
        client,
        vidriera["id"],
        effective_start="2026-12-10",
        effective_end="2026-12-31",
        start_time="21:00",
    )
    assert conflict.status_code == 409
    assert "reemplaza" in conflict.json()["detail"]
    listed = client.get(f"/api/operations/vidrieras/{vidriera['id']}/schedules")
    assert len(listed.json()) == 1
    assert listed.json()[0]["current"]["start_time"] == "22:00:00"

    nylon = _schedule(
        client,
        vidriera["id"],
        operation_type="black_nylon",
        effective_start="2026-12-01",
        effective_end="2026-12-20",
    )
    assert nylon.status_code == 201


def test_revision_keeps_past_expected_times(client: TestClient) -> None:
    vidriera = _vidriera(client)
    today = local_today()
    tomorrow = today + timedelta(days=1)
    created = _schedule(client, vidriera["id"])
    assert created.status_code == 201
    series = created.json()["series_id"]
    revised = client.post(
        f"/api/operations/schedules/{series}/revisions",
        json={
            "effective_from": tomorrow.isoformat(),
            "effective_end": (today + timedelta(days=10)).isoformat(),
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "21:00",
            "end_time": "03:00",
            "notes": "nuevo horario",
        },
    )
    assert revised.status_code == 200
    revisions = revised.json()["revisions"]
    assert revisions[0]["effective_end"] == today.isoformat()
    assert revisions[0]["start_time"] == "22:00:00"
    assert revisions[1]["effective_start"] == tomorrow.isoformat()
    assert revisions[1]["start_time"] == "21:00:00"

    found = _occurrences(
        client,
        vidriera["id"],
        today.isoformat(),
        tomorrow.isoformat(),
        operation_type="artificial_lighting",
    )
    by_day = {item["occurrence_date"]: item for item in found.json()}
    assert by_day[today.isoformat()]["expected_start"].endswith("22:00:00-03:00") or (
        "22:00:00" in by_day[today.isoformat()]["expected_start"]
    )
    assert "21:00:00" in by_day[tomorrow.isoformat()]["expected_start"]
    assert by_day[today.isoformat()]["series_id"] == series
    assert by_day[tomorrow.isoformat()]["series_id"] == series


def test_pause_hides_occurrences_until_resume(client: TestClient) -> None:
    vidriera = _vidriera(client)
    today = local_today()
    created = _schedule(client, vidriera["id"])
    series = created.json()["series_id"]
    pause_on = today + timedelta(days=3)
    resume_on = today + timedelta(days=6)
    paused = client.post(
        f"/api/operations/schedules/{series}/pause",
        json={"effective_from": pause_on.isoformat()},
    )
    assert paused.status_code == 200
    assert paused.json()["current"]["status"] == "paused"
    assert paused.json()["current"]["generates"] is False
    hidden = _occurrences(
        client,
        vidriera["id"],
        pause_on.isoformat(),
        (pause_on + timedelta(days=1)).isoformat(),
    )
    assert hidden.json() == []
    still = _occurrences(client, vidriera["id"], today.isoformat(), today.isoformat())
    assert len(still.json()) == 1
    assert "22:00:00" in still.json()[0]["expected_start"]

    resumed = client.post(
        f"/api/operations/schedules/{series}/resume",
        json={"effective_from": resume_on.isoformat()},
    )
    assert resumed.status_code == 200
    assert resumed.json()["current"]["status"] == "active"
    gap = _occurrences(
        client,
        vidriera["id"],
        pause_on.isoformat(),
        (resume_on - timedelta(days=1)).isoformat(),
    )
    assert gap.json() == []
    back = _occurrences(
        client,
        vidriera["id"],
        resume_on.isoformat(),
        resume_on.isoformat(),
    )
    assert "22:00:00" in back.json()[0]["expected_start"]


def test_ending_shortens_the_period_without_changing_times(client: TestClient) -> None:
    vidriera = _vidriera(client)
    today = local_today()
    created = _schedule(client, vidriera["id"])
    series = created.json()["series_id"]
    closed_on = today + timedelta(days=2)
    ended = client.post(
        f"/api/operations/schedules/{series}/end",
        json={"effective_end": closed_on.isoformat()},
    )
    assert ended.status_code == 200
    current = ended.json()["current"]
    assert current["status"] == "ended"
    assert current["effective_end"] == closed_on.isoformat()
    assert current["start_time"] == "22:00:00"
    assert current["end_time"] == "02:00:00"
    later = _occurrences(
        client,
        vidriera["id"],
        (closed_on + timedelta(days=1)).isoformat(),
        (today + timedelta(days=10)).isoformat(),
    )
    assert later.json() == []
    blocked = client.post(
        f"/api/operations/schedules/{series}/revisions",
        json={
            "effective_from": (today + timedelta(days=1)).isoformat(),
            "effective_end": closed_on.isoformat(),
            "weekdays": [1],
            "start_time": "21:00",
            "end_time": "23:00",
        },
    )
    assert blocked.status_code == 409


def test_rejects_a_same_day_change_after_the_window_ended(client: TestClient) -> None:
    now = utc_now().astimezone(APP_TIMEZONE)
    if now.time() < time(0, 15):
        pytest.skip("demasiado cerca de la medianoche")
    vidriera = _vidriera(client)
    today = local_today()
    created = _schedule(
        client,
        vidriera["id"],
        effective_start=today.isoformat(),
        effective_end=(today + timedelta(days=5)).isoformat(),
        start_time="00:00",
        end_time="00:05",
    )
    assert created.status_code == 201
    series = created.json()["series_id"]
    revised = client.post(
        f"/api/operations/schedules/{series}/revisions",
        json={
            "effective_from": today.isoformat(),
            "effective_end": (today + timedelta(days=5)).isoformat(),
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "01:00",
            "end_time": "02:00",
        },
    )
    assert revised.status_code == 422
    assert "mañana" in revised.json()["detail"]


def test_downgrade_drops_schedules_and_keeps_production_data() -> None:
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    config = _alembic_config()
    try:
        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.begin() as connection:
            quinta_id = uuid.uuid4()
            vidriera_id = uuid.uuid4()
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
        connected.dispose()
        command.downgrade(config, "0004_operations")
        connected = create_engine(url)
        with connected.connect() as connection:
            schedules = connection.scalar(
                text("SELECT to_regclass('public.recurring_operation_schedules')")
            )
            operations = connection.scalar(
                text("SELECT to_regclass('public.operations')")
            )
            code = connection.scalar(
                text("SELECT code FROM vidrieras WHERE id = :id"),
                {"id": vidriera_id},
            )
        connected.dispose()
        assert schedules is None
        assert operations == "operations"
        assert code == "VE-V001"
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)
