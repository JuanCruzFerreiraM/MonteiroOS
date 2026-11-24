import uuid

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from starlette.responses import Response

from app.core.config import get_settings
from app.core.database import get_db_session
from app.main import SCHEMA_NOT_APPLIED_DETAIL, create_app
from app.modules.production import services
from tests.db_isolation import (
    create_isolated_database,
    drop_isolated_database,
    restore_alembic_url,
    use_alembic_url,
)

BACKEND_ROOT = __file__.rsplit("/tests/", 1)[0]


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


def test_creates_a_quinta_and_normalizes_its_code(client: TestClient) -> None:
    response = client.post(
        "/api/production/quintas",
        json={"code": " ve ", "name": "  Villa   Elisa ", "notes": "  camino  "},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "VE"
    assert body["name"] == "Villa Elisa"
    assert body["notes"] == "camino"
    assert body["active"] is True
    assert uuid.UUID(body["id"])

    stored = client.get(f"/api/production/quintas/{body['id']}")
    assert stored.status_code == 200
    assert stored.json()["code"] == "VE"
    assert "boundary" not in stored.json()


def test_rejects_duplicate_and_invalid_quinta_codes(client: TestClient) -> None:
    assert _quinta(client, "VE", "Villa Elisa").status_code == 201
    duplicate = _quinta(client, "ve", "Otra")
    invalid = _quinta(client, "V E", "Nombre")
    short = _quinta(client, "V", "Nombre")

    assert duplicate.status_code == 409
    assert "código" in duplicate.json()["detail"]
    assert invalid.status_code == 422
    assert "2 a 12" in invalid.json()["detail"]
    assert short.status_code == 422


def test_rejects_a_reused_quinta_code_after_deactivation(client: TestClient) -> None:
    created = _quinta(client, "AS", "Arturo Seguí").json()
    deactivated = client.patch(
        f"/api/production/quintas/{created['id']}",
        json={"active": False},
    )
    reused = _quinta(client, "AS", "Otra propiedad")

    assert deactivated.status_code == 200
    assert reused.status_code == 409


def test_lists_active_quintas_and_keeps_inactive_records_readable(
    client: TestClient,
) -> None:
    active = _quinta(client, "VE", "Villa Elisa").json()
    inactive = _quinta(client, "AS", "Arturo Seguí").json()
    client.patch(f"/api/production/quintas/{inactive['id']}", json={"active": False})

    default_list = client.get("/api/production/quintas")
    full_list = client.get("/api/production/quintas?include_inactive=true")
    direct = client.get(f"/api/production/quintas/{inactive['id']}")

    assert [row["code"] for row in default_list.json()] == ["VE"]
    assert {row["code"] for row in full_list.json()} == {"VE", "AS"}
    assert direct.status_code == 200
    assert direct.json()["id"] == inactive["id"]
    assert direct.json()["code"] == "AS"
    assert active["id"] != inactive["id"]


def test_descriptive_edit_preserves_quinta_identity(client: TestClient) -> None:
    created = _quinta(client, "VE", "Villa Elisa").json()
    updated = client.patch(
        f"/api/production/quintas/{created['id']}",
        json={"name": "Villa Elisa norte", "notes": "sobre la ruta"},
    )

    assert updated.status_code == 200
    assert updated.json()["id"] == created["id"]
    assert updated.json()["code"] == "VE"
    assert updated.json()["name"] == "Villa Elisa norte"


def test_rejects_changing_a_quinta_code(client: TestClient) -> None:
    created = _quinta(client, "VE", "Villa Elisa").json()
    response = client.patch(
        f"/api/production/quintas/{created['id']}",
        json={"code": "AS"},
    )

    assert response.status_code == 409
    assert client.get(f"/api/production/quintas/{created['id']}").json()["code"] == "VE"


def test_creates_a_vidriera_with_exactly_four_canteros(client: TestClient) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    response = _vidriera(client, quinta["id"], "ve-v001", "Norte")

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "VE-V001"
    assert body["quinta_id"] == quinta["id"]
    assert [cantero["number"] for cantero in body["canteros"]] == [1, 2, 3, 4]
    assert [cantero["display_code"] for cantero in body["canteros"]] == [
        "VE-V001-C1",
        "VE-V001-C2",
        "VE-V001-C3",
        "VE-V001-C4",
    ]
    assert len({cantero["id"] for cantero in body["canteros"]}) == 4

    again = client.get(f"/api/production/vidrieras/{body['id']}")
    assert again.status_code == 200
    assert again.json()["canteros"][3]["display_code"] == "VE-V001-C4"


def test_code_suggestion_skips_used_numbers_and_does_not_renumber(
    client: TestClient,
) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    first_suggestion = client.get(
        f"/api/production/quintas/{quinta['id']}/vidrieras/next-code"
    )
    created = _vidriera(client, quinta["id"], "VE-V001", "Norte").json()
    skipped = _vidriera(client, quinta["id"], "VE-V005", "Sur")
    suggestion = client.get(
        f"/api/production/quintas/{quinta['id']}/vidrieras/next-code"
    )

    assert first_suggestion.json() == {"code": "VE-V001", "number": 1}
    assert skipped.status_code == 201
    assert suggestion.json() == {"code": "VE-V006", "number": 6}
    assert client.get(f"/api/production/vidrieras/{created['id']}").json()["code"] == (
        "VE-V001"
    )


def test_does_not_reuse_a_vidriera_code_after_deactivation(client: TestClient) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    created = _vidriera(client, quinta["id"], "VE-V001", "Norte").json()
    client.patch(f"/api/production/vidrieras/{created['id']}", json={"active": False})

    reused = _vidriera(client, quinta["id"], "VE-V001", "Otra")
    suggestion = client.get(
        f"/api/production/quintas/{quinta['id']}/vidrieras/next-code"
    )
    direct = client.get(f"/api/production/vidrieras/{created['id']}")
    visible = client.get(f"/api/production/quintas/{quinta['id']}/vidrieras")

    assert reused.status_code == 409
    assert suggestion.json()["code"] == "VE-V002"
    assert direct.status_code == 200
    assert direct.json()["code"] == "VE-V001"
    assert visible.json() == []


def test_vidriera_names_are_unique_inside_a_quinta_only(client: TestClient) -> None:
    first = _quinta(client, "VE", "Villa Elisa").json()
    second = _quinta(client, "AS", "Arturo Seguí").json()
    original = _vidriera(client, first["id"], "VE-V001", "Norte")
    duplicate = _vidriera(client, first["id"], "VE-V002", " norte ")
    other_quinta = _vidriera(client, second["id"], "AS-V001", "Norte")

    assert original.status_code == 201
    assert duplicate.status_code == 409
    assert other_quinta.status_code == 201


def test_rejects_invalid_vidriera_codes_and_unknown_parents(client: TestClient) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    missing = uuid.uuid4()

    assert _vidriera(client, quinta["id"], "AS-V001", "Norte").status_code == 422
    assert _vidriera(client, quinta["id"], "VE-V0001", "Norte").status_code == 422
    assert _vidriera(client, quinta["id"], "VE-V1000", "Lejos").status_code == 201
    assert _vidriera(client, missing, "VE-V001", "Norte").status_code == 404
    assert client.get(f"/api/production/quintas/{missing}").status_code == 404


def test_rejects_a_parent_change_and_keeps_identity_on_rename(
    client: TestClient,
) -> None:
    primera = _quinta(client, "VE", "Villa Elisa").json()
    segunda = _quinta(client, "AS", "Arturo Seguí").json()
    vidriera = _vidriera(client, primera["id"], "VE-V001", "Norte").json()
    moved = client.patch(
        f"/api/production/vidrieras/{vidriera['id']}",
        json={"quinta_id": segunda["id"], "name": "Movida"},
    )
    renamed = client.patch(
        f"/api/production/vidrieras/{vidriera['id']}",
        json={"name": "Norte nuevo", "code": "VE-V009"},
    )
    stored = client.get(f"/api/production/vidrieras/{vidriera['id']}").json()

    assert moved.status_code == 409
    assert renamed.status_code == 409
    assert stored["id"] == vidriera["id"]
    assert stored["quinta_id"] == primera["id"]
    assert stored["code"] == "VE-V001"
    assert stored["name"] == "Norte"


def test_cannot_reactivate_a_vidriera_while_its_quinta_is_inactive(
    client: TestClient,
) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    vidriera = _vidriera(client, quinta["id"], "VE-V001", "Norte").json()
    client.patch(f"/api/production/vidrieras/{vidriera['id']}", json={"active": False})
    client.patch(f"/api/production/quintas/{quinta['id']}", json={"active": False})

    response = client.patch(
        f"/api/production/vidrieras/{vidriera['id']}",
        json={"active": True},
    )

    assert response.status_code == 409
    stored = client.get(f"/api/production/vidrieras/{vidriera['id']}")
    assert stored.json()["active"] is False
    assert stored.json()["code"] == "VE-V001"


def test_rejects_a_duplicated_quinta_name(client: TestClient) -> None:
    assert _quinta(client, "VE", "Villa Elisa").status_code == 201
    duplicate = _quinta(client, "AS", " villa   elisa ")

    assert duplicate.status_code == 409
    assert "nombre" in duplicate.json()["detail"]


def test_rejects_creates_under_an_inactive_quinta(client: TestClient) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    client.patch(f"/api/production/quintas/{quinta['id']}", json={"active": False})

    created = _vidriera(client, quinta["id"], "VE-V001", "Norte")
    suggestion = client.get(
        f"/api/production/quintas/{quinta['id']}/vidrieras/next-code"
    )

    assert created.status_code == 409
    assert suggestion.status_code == 409


def test_edits_cantero_name_without_changing_its_number(client: TestClient) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    vidriera = _vidriera(client, quinta["id"], "VE-V001", "Norte").json()
    cantero = vidriera["canteros"][0]
    renamed = client.patch(
        f"/api/production/canteros/{cantero['id']}",
        json={"name": "  Contra  el alambrado "},
    )
    conflict = client.patch(
        f"/api/production/canteros/{vidriera['canteros'][1]['id']}",
        json={"name": "contra el alambrado"},
    )
    renumbered = client.patch(
        f"/api/production/canteros/{cantero['id']}",
        json={"number": 4},
    )
    stored = client.get(f"/api/production/vidrieras/{vidriera['id']}").json()

    assert renamed.status_code == 200
    assert renamed.json()["display_code"] == "VE-V001-C1"
    assert renamed.json()["name"] == "Contra el alambrado"
    assert renamed.json()["id"] == cantero["id"]
    assert conflict.status_code == 409
    assert renumbered.status_code == 409
    assert stored["canteros"][0]["number"] == 1
    assert stored["canteros"][0]["name"] == "Contra el alambrado"


def test_cantero_failure_does_not_leave_a_partial_vidriera(
    client: TestClient,
    engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    monkeypatch.setattr(services, "CANTERO_NUMBERS", (1, 2, 3, 5))

    response = _vidriera(client, quinta["id"], "VE-V001", "Norte")

    assert response.status_code == 409
    with Session(engine) as session:
        count = session.scalar(text("SELECT count(*) FROM vidrieras"))
    assert count == 0


def test_delete_is_not_offered_for_physical_records(client: TestClient) -> None:
    quinta = _quinta(client, "VE", "Villa Elisa").json()
    vidriera = _vidriera(client, quinta["id"], "VE-V001", "Norte").json()

    assert client.delete(f"/api/production/quintas/{quinta['id']}").status_code == 405
    assert (
        client.delete(f"/api/production/vidrieras/{vidriera['id']}").status_code == 405
    )
    assert client.get(f"/api/production/vidrieras/{vidriera['id']}").status_code == 200


def test_access_secret_protects_production_routes(
    engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ACCESS_SECRET", "test-secret")
    get_settings.cache_clear()
    sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_session():
        session = sessions()
        try:
            yield session
        finally:
            session.close()

    try:
        application = create_app()
        application.dependency_overrides[get_db_session] = override_session
        with TestClient(application) as protected:
            denied = protected.get("/api/production/quintas")
            allowed = protected.get(
                "/api/production/quintas",
                headers={"X-Monteiro-Access": "test-secret"},
            )
            health = protected.get("/health")
    finally:
        get_settings.cache_clear()

    assert denied.status_code == 401
    assert allowed.status_code == 200
    assert allowed.json() == []
    assert health.status_code == 200


def test_missing_schema_does_not_look_like_an_empty_farm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ACCESS_SECRET", "")
    get_settings.cache_clear()
    name, url = create_isolated_database()
    connected = create_engine(url, pool_pre_ping=True)
    sessions = sessionmaker(bind=connected, autoflush=False, expire_on_commit=False)

    def override_session():
        session = sessions()
        try:
            yield session
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[get_db_session] = override_session
    try:
        with TestClient(application, raise_server_exceptions=False) as test_client:
            listing = test_client.get("/api/production/quintas")
            created = test_client.post(
                "/api/production/quintas",
                json={"code": "VE", "name": "Villa Elisa"},
            )
    finally:
        get_settings.cache_clear()
        connected.dispose()
        drop_isolated_database(name)

    assert listing.status_code == 503
    assert listing.json() == {"detail": SCHEMA_NOT_APPLIED_DETAIL}
    assert "SELECT" not in listing.text
    assert "psycopg" not in listing.text
    assert created.status_code == 503
    assert created.json()["detail"] == SCHEMA_NOT_APPLIED_DETAIL


def test_migration_upgrade_downgrade_and_database_constraints() -> None:
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    config = _alembic_config()
    try:
        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.begin() as connection:
            constraints = set(
                connection.scalars(
                    text(
                        "SELECT conname FROM pg_constraint "
                        "WHERE connamespace = 'public'::regnamespace"
                    )
                )
            )
            columns = set(
                connection.scalars(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema = 'public'"
                    )
                )
            )
            boundary_tables = set(
                connection.scalars(
                    text(
                        "SELECT table_name FROM information_schema.columns "
                        "WHERE table_schema = 'public' AND column_name = 'boundary'"
                    )
                )
            )
            quinta_id = uuid.uuid4()
            connection.execute(
                text(
                    "INSERT INTO quintas (id, code, name, name_key, active) "
                    "VALUES (:id, 'VE', 'Villa', 'villa', true)"
                ),
                {"id": quinta_id},
            )
            vidriera_id = uuid.uuid4()
            connection.execute(
                text(
                    "INSERT INTO vidrieras "
                    "(id, quinta_id, code, number, name, name_key, active) "
                    "VALUES (:id, :quinta_id, 'VE-V001', 1, 'Norte', 'norte', true)"
                ),
                {"id": vidriera_id, "quinta_id": quinta_id},
            )
        with pytest.raises(IntegrityError):
            with connected.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO quintas (id, code, name, name_key, active) "
                        "VALUES (:id, 'VE', 'Otra', 'otra', false)"
                    ),
                    {"id": uuid.uuid4()},
                )
        with pytest.raises(IntegrityError):
            with connected.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO vidrieras "
                        "(id, quinta_id, code, number, name, name_key, active) "
                        "VALUES (:id, :quinta_id, 'VE-V001', 1, 'Sur', 'sur', true)"
                    ),
                    {"id": uuid.uuid4(), "quinta_id": quinta_id},
                )
        with pytest.raises(IntegrityError):
            with connected.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO canteros (id, vidriera_id, number, active) "
                        "VALUES (:id, :vidriera_id, 5, true)"
                    ),
                    {"id": uuid.uuid4(), "vidriera_id": vidriera_id},
                )
        with pytest.raises(IntegrityError):
            with connected.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO vidrieras "
                        "(id, quinta_id, code, number, name, name_key, active) "
                        "VALUES (:id, :quinta_id, 'VE-V002', 2, 'Huérfana', "
                        "'huerfana', true)"
                    ),
                    {"id": uuid.uuid4(), "quinta_id": uuid.uuid4()},
                )
        connected.dispose()

        assert "uq_quintas_code" in constraints
        assert "uq_vidrieras_code" in constraints
        assert "uq_vidrieras_quinta_number" in constraints
        assert "uq_vidrieras_quinta_name" in constraints
        assert "uq_canteros_vidriera_number" in constraints
        assert "ck_canteros_number" in constraints
        assert "geometry" not in columns
        assert boundary_tables == {"quintas", "vidrieras"}

        command.downgrade(config, "base")
        connected = create_engine(url)
        with connected.connect() as connection:
            remaining = connection.scalar(text("SELECT to_regclass('public.quintas')"))
        connected.dispose()
        assert remaining is None
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)


def _alembic_config() -> Config:
    return Config(f"{BACKEND_ROOT}/alembic.ini")


def _quinta(client: TestClient, code: str, name: str) -> Response:
    return client.post(
        "/api/production/quintas",
        json={"code": code, "name": name},
    )


def _vidriera(
    client: TestClient,
    quinta_id: uuid.UUID,
    code: str,
    name: str,
):
    return client.post(
        f"/api/production/quintas/{quinta_id}/vidrieras",
        json={"code": code, "name": name},
    )
