import uuid

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
        json={"code": "VE", "name": "Villa Elisa"},
    )
    assert quinta.status_code == 201
    created = client.post(
        f"/api/production/quintas/{quinta.json()['id']}/vidrieras",
        json={"code": "VE-V001", "name": "Norte"},
    )
    assert created.status_code == 201
    return created.json()


def _cycle(client: TestClient, vidriera_id: str, start: str, end: str | None = None):
    created = client.post(
        f"/api/production/vidrieras/{vidriera_id}/cycles",
        json={"start_date": start},
    )
    assert created.status_code == 201
    if end is None:
        return created.json()
    closed = client.post(
        f"/api/production/cycles/{created.json()['id']}/finalize",
        json={"end_date": end},
    )
    assert closed.status_code == 200
    return closed.json()


def _operation(client: TestClient, vidriera_id: str, **extra) -> dict:
    body = {
        "operation_type": "irrigation",
        "occurred_at": "2024-06-01T15:00:00-03:00",
    }
    body.update(extra)
    created = client.post(
        f"/api/operations/vidrieras/{vidriera_id}/operations",
        json=body,
    )
    assert created.status_code == 201
    return created.json()


def _history(client: TestClient, vidriera_id: str, **params) -> dict:
    response = client.get(
        f"/api/operations/vidrieras/{vidriera_id}/operations",
        params=params,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_orders_by_occurrence_time_and_keeps_that_order_after_an_edit(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    earlier = _operation(client, vidriera["id"])
    later = _operation(
        client,
        vidriera["id"],
        occurred_at="2024-06-03T09:00:00-03:00",
        notes="después",
    )
    edited = client.patch(
        f"/api/operations/operations/{earlier['id']}",
        json={"notes": "corregida más tarde"},
    )
    assert edited.status_code == 200

    listed = _history(client, vidriera["id"])
    assert [item["id"] for item in listed["items"]] == [later["id"], earlier["id"]]
    assert listed["next_cursor"] is None


def test_filters_argentine_dates_including_an_overnight_start(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    late = _operation(
        client,
        vidriera["id"],
        operation_type="artificial_lighting",
        occurred_at="2024-06-01T23:30:00-03:00",
        interval_start="2024-06-01T23:30:00-03:00",
        interval_end="2024-06-02T02:00:00-03:00",
    )
    after_midnight = _operation(
        client,
        vidriera["id"],
        occurred_at="2024-06-02T00:10:00-03:00",
    )

    first_day = _history(
        client,
        vidriera["id"],
        **{"from": "2024-06-01", "to": "2024-06-01"},
    )
    second_day = _history(
        client,
        vidriera["id"],
        **{"from": "2024-06-02", "to": "2024-06-02"},
    )
    backwards = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/operations",
        params={"from": "2024-06-03", "to": "2024-06-01"},
    )

    assert [item["id"] for item in first_day["items"]] == [late["id"]]
    assert [item["id"] for item in second_day["items"]] == [after_midnight["id"]]
    assert backwards.status_code == 422
    assert "hasta" in backwards.json()["detail"]


def test_filters_by_type_cycle_and_explicit_absence_of_a_cycle(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    finalized = _cycle(client, vidriera["id"], "2024-01-01", "2024-03-01")
    active = _cycle(client, vidriera["id"], "2024-05-01")
    irrigation = _operation(client, vidriera["id"], cycle_id=finalized["id"])
    observation = _operation(
        client,
        vidriera["id"],
        operation_type="observation",
        occurred_at="2024-06-02T11:00:00-03:00",
        cycle_id=active["id"],
    )
    preparation = _operation(
        client,
        vidriera["id"],
        operation_type="manual_labor",
        occurred_at="2024-04-15T08:00:00-03:00",
    )

    by_type = _history(client, vidriera["id"], operation_type="irrigation")
    by_finalized = _history(client, vidriera["id"], cycle=finalized["id"])
    without_cycle = _history(client, vidriera["id"], cycle="none")
    unknown_type = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/operations",
        params={"operation_type": "harvest"},
    )

    assert [item["id"] for item in by_type["items"]] == [irrigation["id"]]
    assert [item["id"] for item in by_finalized["items"]] == [irrigation["id"]]
    assert by_finalized["items"][0]["cycle_id"] == finalized["id"]
    assert [item["id"] for item in without_cycle["items"]] == [preparation["id"]]
    assert observation["id"] not in [item["id"] for item in without_cycle["items"]]
    assert unknown_type.status_code == 422


def test_pages_without_skipping_or_repeating_tied_timestamps(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    created = [
        _operation(
            client,
            vidriera["id"],
            occurred_at="2024-06-01T15:00:00-03:00",
            notes=str(index),
        )
        for index in range(5)
    ]
    seen: list[str] = []
    cursor = None
    pages = 0
    while True:
        params = {"limit": 2}
        if cursor is not None:
            params["cursor"] = cursor
        page = _history(client, vidriera["id"], **params)
        pages += 1
        seen.extend(item["id"] for item in page["items"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
        assert pages < 6

    assert pages == 3
    assert seen == sorted(
        (item["id"] for item in created),
        key=uuid.UUID,
        reverse=True,
    )
    assert len(seen) == len(set(seen)) == 5
    invalid = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/operations",
        params={"cursor": "no-es-un-cursor"},
    )
    assert invalid.status_code == 422


def test_completed_history_omits_unverified_and_rejected_occurrences(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    schedule = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/schedules",
        json={
            "operation_type": "artificial_lighting",
            "effective_start": "2024-06-01",
            "effective_end": "2024-06-03",
            "weekdays": [1, 2, 3, 4, 5, 6, 7],
            "start_time": "22:00",
            "end_time": "02:00",
        },
    )
    assert schedule.status_code == 201
    series = schedule.json()["series_id"]
    confirmed = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve",
        json={
            "series_id": series,
            "occurrence_date": "2024-06-01",
            "outcome": "confirmed",
        },
    )
    rejected = client.post(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences/resolve",
        json={
            "series_id": series,
            "occurrence_date": "2024-06-02",
            "outcome": "not_occurred",
        },
    )
    assert confirmed.status_code == 200
    assert rejected.status_code == 200
    manual = _operation(client, vidriera["id"])

    history = _history(client, vidriera["id"])
    occurrences = client.get(
        f"/api/operations/vidrieras/{vidriera['id']}/occurrences",
        params={"from": "2024-06-01", "to": "2024-06-03"},
    )
    statuses = {item["occurrence_date"]: item["status"] for item in occurrences.json()}

    assert [item["id"] for item in history["items"]] == [
        confirmed.json()["operation_id"],
        manual["id"],
    ]
    assert {item["origin"] for item in history["items"]} == {"manual", "scheduled"}
    assert statuses == {
        "2024-06-01": "confirmed",
        "2024-06-02": "not_occurred",
        "2024-06-03": "unverified",
    }
    assert uuid.UUID(confirmed.json()["operation_id"])
