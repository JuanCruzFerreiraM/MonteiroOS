import uuid
from datetime import date

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import get_db_session
from app.main import create_app
from app.modules.production import cycles
from app.modules.production.rules import DomainError
from app.modules.production.schemas import CycleStart
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


def _start(client: TestClient, vidriera_id: str, start: str, notes: str | None = None):
    body: dict[str, str] = {"start_date": start}
    if notes is not None:
        body["notes"] = notes
    return client.post(f"/api/production/vidrieras/{vidriera_id}/cycles", json=body)


def _finalize(client: TestClient, cycle_id: str, end: str):
    return client.post(
        f"/api/production/cycles/{cycle_id}/finalize",
        json={"end_date": end},
    )


def test_starts_the_first_cycle_without_crop_fields(client: TestClient) -> None:
    vidriera = _vidriera(client)
    created = _start(client, vidriera["id"], "2024-09-15", notes="  plantación  ")

    assert created.status_code == 201
    body = created.json()
    assert body["vidriera_id"] == vidriera["id"]
    assert body["start_date"] == "2024-09-15"
    assert body["end_date"] is None
    assert body["status"] == "active"
    assert body["notes"] == "plantación"
    assert "variety" not in body
    assert uuid.UUID(body["id"])

    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles")
    assert listed.status_code == 200
    assert listed.json()["active"]["id"] == body["id"]
    assert listed.json()["history"] == []
    active = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles/active")
    assert active.status_code == 200
    assert active.json()["id"] == body["id"]
    detail = client.get(f"/api/production/vidrieras/{vidriera['id']}")
    assert detail.status_code == 200
    assert len(detail.json()["canteros"]) == 4
    assert detail.json()["code"] == "VE-V001"


def test_an_existing_vidriera_without_cycles_is_empty(client: TestClient) -> None:
    vidriera = _vidriera(client)
    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles")
    active = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles/active")

    assert listed.status_code == 200
    assert listed.json() == {"active": None, "history": []}
    assert active.status_code == 404
    assert active.json()["detail"] == "Esta vidriera no tiene un ciclo activo."


def test_a_missing_vidriera_is_not_an_empty_cycle_list(client: TestClient) -> None:
    missing = uuid.uuid4()
    listed = client.get(f"/api/production/vidrieras/{missing}/cycles")
    started = _start(client, str(missing), "2024-01-01")
    active = client.get(f"/api/production/vidrieras/{missing}/cycles/active")

    assert listed.status_code == 404
    assert listed.json()["detail"] == "No se encontró la vidriera."
    assert started.status_code == 404
    assert active.status_code == 404
    assert active.json()["detail"] == "No se encontró la vidriera."


def test_two_vidrieras_can_have_active_cycles_at_once(client: TestClient) -> None:
    first = _vidriera(client, "VE", "Villa Elisa")
    second = _vidriera(client, "AS", "Arturo Seguí")

    left = _start(client, first["id"], "2024-01-01")
    right = _start(client, second["id"], "2024-01-01")

    assert left.status_code == 201
    assert right.status_code == 201
    assert left.json()["id"] != right.json()["id"]


def test_a_second_active_cycle_is_rejected_and_names_the_current_one(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    current = _start(client, vidriera["id"], "2024-01-15").json()
    rejected = _start(client, vidriera["id"], "2024-06-01")
    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles").json()

    assert rejected.status_code == 409
    assert current["id"] in rejected.json()["detail"]
    assert "2024-01-15" in rejected.json()["detail"]
    assert listed["active"]["id"] == current["id"]
    assert listed["history"] == []


def test_finalizing_keeps_the_record_and_allows_the_next_cycle(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    started = _start(client, vidriera["id"], "2024-01-01").json()
    closed = _finalize(client, started["id"], "2024-03-02")

    assert closed.status_code == 200
    assert closed.json()["id"] == started["id"]
    assert closed.json()["status"] == "finalized"
    assert closed.json()["end_date"] == "2024-03-02"
    assert closed.json()["vidriera_id"] == vidriera["id"]

    active = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles/active")
    assert active.status_code == 404
    stored = client.get(f"/api/production/cycles/{started['id']}")
    assert stored.status_code == 200
    assert stored.json()["end_date"] == "2024-03-02"

    following = _start(client, vidriera["id"], "2024-03-03")
    assert following.status_code == 201
    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles").json()
    assert listed["active"]["id"] == following.json()["id"]
    assert [item["id"] for item in listed["history"]] == [started["id"]]


def test_history_is_ordered_by_planting_date_descending(client: TestClient) -> None:
    vidriera = _vidriera(client)
    older = _start(client, vidriera["id"], "2023-01-01").json()
    assert _finalize(client, older["id"], "2023-02-01").status_code == 200
    newer = _start(client, vidriera["id"], "2024-01-01").json()
    assert _finalize(client, newer["id"], "2024-02-01").status_code == 200

    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles").json()
    assert listed["active"] is None
    assert [item["id"] for item in listed["history"]] == [newer["id"], older["id"]]


def test_rejects_an_end_before_planting_and_a_second_finalization(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    started = _start(client, vidriera["id"], "2024-03-02").json()
    too_early = _finalize(client, started["id"], "2024-03-01")
    same_day = _finalize(client, started["id"], "2024-03-02")
    again = _finalize(client, started["id"], "2024-04-01")

    assert too_early.status_code == 422
    assert "anterior" in too_early.json()["detail"]
    assert same_day.status_code == 200
    assert same_day.json()["status"] == "finalized"
    assert again.status_code == 409
    assert "ya está finalizado" in again.json()["detail"]
    stored = client.get(f"/api/production/cycles/{started['id']}").json()
    assert stored["end_date"] == "2024-03-02"


def test_rejects_an_overlapping_historical_period(client: TestClient) -> None:
    vidriera = _vidriera(client)
    previous = _start(client, vidriera["id"], "2024-01-01").json()
    assert _finalize(client, previous["id"], "2024-03-01").status_code == 200

    shared_day = _start(client, vidriera["id"], "2024-03-01")
    assert shared_day.status_code == 409
    assert previous["id"] in shared_day.json()["detail"]
    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles").json()
    assert listed["active"] is None
    assert len(listed["history"]) == 1

    following = _start(client, vidriera["id"], "2024-03-02")
    assert following.status_code == 201


def test_opening_a_vidriera_does_not_create_a_cycle(client: TestClient) -> None:
    vidriera = _vidriera(client)
    opened = client.get(f"/api/production/vidrieras/{vidriera['id']}")
    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles")

    assert opened.status_code == 200
    assert listed.json() == {"active": None, "history": []}


def test_unknown_cycle_and_invalid_dates_are_rejected(client: TestClient) -> None:
    missing = client.get(f"/api/production/cycles/{uuid.uuid4()}")
    invalid = _start(client, str(uuid.uuid4()), "2024-13-40")
    blank = client.post(
        f"/api/production/vidrieras/{uuid.uuid4()}/cycles",
        json={"notes": "sin fecha"},
    )
    extra = client.post(
        f"/api/production/vidrieras/{uuid.uuid4()}/cycles",
        json={"start_date": "2024-01-01", "variety": "Snow"},
    )

    assert missing.status_code == 404
    assert missing.json()["detail"] == "No se encontró el ciclo."
    assert invalid.status_code == 422
    assert "AAAA-MM-DD" in invalid.json()["detail"]
    assert blank.status_code == 422
    assert "plantación" in blank.json()["detail"]
    assert extra.status_code == 422
    assert "variedad" in extra.json()["detail"]


def test_corrections_keep_identity_and_reject_overlaps(client: TestClient) -> None:
    vidriera = _vidriera(client)
    other = _vidriera(client, "AS", "Arturo Seguí")
    first = _start(client, vidriera["id"], "2024-01-01", notes="inicial").json()
    assert _finalize(client, first["id"], "2024-03-01").status_code == 200
    second = _start(client, vidriera["id"], "2024-04-01").json()

    moved = client.patch(
        f"/api/production/cycles/{second['id']}",
        json={"start_date": "2024-03-02", "notes": "  corregida  "},
    )
    overlapping = client.patch(
        f"/api/production/cycles/{second['id']}",
        json={"start_date": "2024-03-01"},
    )
    ownership = client.patch(
        f"/api/production/cycles/{second['id']}",
        json={"vidriera_id": other["id"]},
    )
    identity = client.patch(
        f"/api/production/cycles/{second['id']}",
        json={"id": str(uuid.uuid4())},
    )
    closing = client.patch(
        f"/api/production/cycles/{second['id']}",
        json={"end_date": "2024-05-01"},
    )
    reopened = client.patch(
        f"/api/production/cycles/{first['id']}",
        json={"end_date": None},
    )
    stored = client.get(f"/api/production/cycles/{second['id']}").json()
    previous = client.get(f"/api/production/cycles/{first['id']}").json()

    assert moved.status_code == 200
    assert moved.json()["id"] == second["id"]
    assert moved.json()["vidriera_id"] == vidriera["id"]
    assert moved.json()["status"] == "active"
    assert moved.json()["start_date"] == "2024-03-02"
    assert moved.json()["end_date"] is None
    assert moved.json()["notes"] == "corregida"
    assert overlapping.status_code == 409
    assert first["id"] in overlapping.json()["detail"]
    assert ownership.status_code == 409
    assert identity.status_code == 409
    assert closing.status_code == 409
    assert "finalizarlo" in closing.json()["detail"]
    assert reopened.status_code == 409
    assert "no reabre" in reopened.json()["detail"]
    assert stored["start_date"] == "2024-03-02"
    assert stored["status"] == "active"
    assert stored["vidriera_id"] == vidriera["id"]
    assert previous["status"] == "finalized"
    assert previous["end_date"] == "2024-03-01"


def test_a_finalized_cycle_can_change_dates_without_reopening(
    client: TestClient,
) -> None:
    vidriera = _vidriera(client)
    cycle = _start(client, vidriera["id"], "2024-01-01").json()
    assert _finalize(client, cycle["id"], "2024-02-01").status_code == 200
    corrected = client.patch(
        f"/api/production/cycles/{cycle['id']}",
        json={"start_date": "2024-01-05", "end_date": "2024-02-10", "notes": "ajuste"},
    )
    too_early = client.patch(
        f"/api/production/cycles/{cycle['id']}",
        json={"end_date": "2024-01-01"},
    )

    assert corrected.status_code == 200
    assert corrected.json()["status"] == "finalized"
    assert corrected.json()["start_date"] == "2024-01-05"
    assert corrected.json()["end_date"] == "2024-02-10"
    assert corrected.json()["id"] == cycle["id"]
    assert too_early.status_code == 422
    stored = client.get(f"/api/production/cycles/{cycle['id']}").json()
    assert stored["end_date"] == "2024-02-10"
    assert stored["status"] == "finalized"


def test_database_conflict_names_the_active_cycle_and_rolls_back(
    engine,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vidriera = _vidriera(client)
    current = _start(client, vidriera["id"], "2024-01-01").json()
    monkeypatch.setattr(
        cycles,
        "_reject_known_conflicts",
        lambda *args, **kwargs: None,
    )
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        with pytest.raises(DomainError) as error:
            cycles.start_cycle(
                session,
                uuid.UUID(vidriera["id"]),
                CycleStart(start_date=date(2024, 8, 1)),
            )
    finally:
        session.close()

    with engine.connect() as connection:
        remaining = connection.scalar(text("SELECT count(*) FROM cultivation_cycles"))
    listed = client.get(f"/api/production/vidrieras/{vidriera['id']}/cycles").json()

    assert error.value.status_code == 409
    assert current["id"] in error.value.detail
    assert remaining == 1
    assert listed["active"]["id"] == current["id"]
    assert listed["history"] == []
