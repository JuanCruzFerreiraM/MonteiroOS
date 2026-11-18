import uuid

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import get_db_session
from app.main import SCHEMA_NOT_APPLIED_DETAIL, create_app
from app.modules.production.geometry import parse_polygon
from tests.db_isolation import (
    create_isolated_database,
    drop_isolated_database,
    restore_alembic_url,
    use_alembic_url,
)

BACKEND_ROOT = __file__.rsplit("/tests/", 1)[0]

QUINTA = [
    [-58.0, -35.0],
    [-57.0, -35.0],
    [-57.0, -34.0],
    [-58.0, -34.0],
    [-58.0, -35.0],
]
INSIDE = [
    [-58.0, -34.75],
    [-57.5, -34.75],
    [-57.5, -34.25],
    [-58.0, -34.25],
    [-58.0, -34.75],
]
OVERLAP = [
    [-57.75, -34.75],
    [-57.25, -34.75],
    [-57.25, -34.25],
    [-57.75, -34.25],
    [-57.75, -34.75],
]
MINOR_OVERFLOW = [
    [-57.75, -34.75],
    [-56.875, -34.75],
    [-56.875, -34.25],
    [-57.75, -34.25],
    [-57.75, -34.75],
]
LARGE_OVERFLOW = [
    [-57.5, -34.75],
    [-56.0, -34.75],
    [-56.0, -34.25],
    [-57.5, -34.25],
    [-57.5, -34.75],
]
DISCONNECTED = [
    [-56.0, -33.0],
    [-55.5, -33.0],
    [-55.5, -32.5],
    [-56.0, -32.5],
    [-56.0, -33.0],
]
BOWTIE = [
    [-58.0, -35.0],
    [-57.0, -34.0],
    [-58.0, -34.0],
    [-57.0, -35.0],
    [-58.0, -35.0],
]
TRIANGLE = [
    [-58.0, -35.0],
    [-57.0, -35.0],
    [-58.0, -34.0],
    [-58.0, -35.0],
]
OUTSIDE_BBOX = [
    [-57.25, -34.25],
    [-57.0625, -34.25],
    [-57.0625, -34.0625],
    [-57.25, -34.0625],
    [-57.25, -34.25],
]


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


def test_parse_rejects_invalid_polygons() -> None:
    with pytest.raises(Exception, match="MultiPolygon"):
        parse_polygon({"type": "MultiPolygon", "coordinates": []})
    with pytest.raises(Exception, match="huecos"):
        parse_polygon({"type": "Polygon", "coordinates": [QUINTA, QUINTA]})
    with pytest.raises(Exception, match="cerrarse"):
        parse_polygon({"type": "Polygon", "coordinates": [QUINTA[:-1]]})
    with pytest.raises(Exception, match="longitud"):
        parse_polygon(
            {
                "type": "Polygon",
                "coordinates": [
                    [[-35.0, -100.0], [-34.0, -100.0], [-34.0, -99.0], [-35.0, -100.0]]
                ],
            }
        )
    with pytest.raises(Exception, match="cruza"):
        parse_polygon({"type": "Polygon", "coordinates": [BOWTIE]})
    with pytest.raises(Exception, match="vértices distintos"):
        parse_polygon(
            {
                "type": "Polygon",
                "coordinates": [
                    [[-58.0, -35.0], [-58.0, -35.0], [-57.0, -35.0], [-58.0, -35.0]]
                ],
            }
        )


def test_saves_edits_and_removes_a_quinta_boundary(client: TestClient, engine) -> None:
    created = client.post(
        "/api/production/quintas",
        json={"code": "VE", "name": "Villa Elisa", "notes": "camino"},
    )
    assert created.status_code == 201
    quinta_id = created.json()["id"]
    assert "boundary" not in created.json()

    missing = client.get(f"/api/production/quintas/{quinta_id}/boundary")
    assert missing.status_code == 200
    assert missing.json()["geometry"] is None
    assert missing.json()["warnings"] == []

    saved = client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(QUINTA)},
    )
    assert saved.status_code == 200
    assert saved.json()["geometry"]["coordinates"] == [QUINTA]
    assert saved.json()["warnings"] == []

    edited = client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(INSIDE), "mode": "replace"},
    )
    assert edited.status_code == 200
    assert edited.json()["geometry"]["coordinates"] == [INSIDE]

    record = client.get(f"/api/production/quintas/{quinta_id}").json()
    assert record["id"] == quinta_id
    assert record["code"] == "VE"
    assert record["notes"] == "camino"
    assert _counts(engine) == {"quintas": 1, "vidrieras": 0, "canteros": 0}

    restarted = create_engine(engine.url)
    with restarted.connect() as connection:
        stored = connection.scalar(
            text("SELECT boundary FROM quintas WHERE id = :id"),
            {"id": quinta_id},
        )
    restarted.dispose()
    assert stored == {"type": "Polygon", "coordinates": [INSIDE]}

    removed = client.delete(f"/api/production/quintas/{quinta_id}/boundary")
    assert removed.status_code == 204
    assert removed.content == b""
    assert (
        client.get(f"/api/production/quintas/{quinta_id}/boundary").json()["geometry"]
        is None
    )
    assert client.get(f"/api/production/quintas/{quinta_id}").status_code == 200


def test_invalid_polygon_does_not_replace_the_saved_boundary(
    client: TestClient,
) -> None:
    quinta_id = _quinta_id(client)
    assert (
        client.put(
            f"/api/production/quintas/{quinta_id}/boundary",
            json={"geometry": _polygon(QUINTA)},
        ).status_code
        == 200
    )

    rejected = client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(BOWTIE)},
    )
    assert rejected.status_code == 422
    assert "cruza" in rejected.json()["detail"]
    assert "SELECT" not in rejected.text
    current = client.get(f"/api/production/quintas/{quinta_id}/boundary").json()
    assert current["geometry"]["coordinates"] == [QUINTA]


def test_unknown_records_are_not_treated_as_unmapped(client: TestClient) -> None:
    unknown = uuid.uuid4()
    assert client.get(f"/api/production/quintas/{unknown}/boundary").status_code == 404
    assert (
        client.get(f"/api/production/vidrieras/{unknown}/boundary").status_code == 404
    )
    assert (
        client.put(
            f"/api/production/vidrieras/{unknown}/boundary",
            json={"geometry": _polygon(INSIDE)},
        ).status_code
        == 404
    )
    removed = client.delete(f"/api/production/quintas/{unknown}/boundary")
    assert removed.status_code == 404
    assert "No se encontró" in removed.json()["detail"]


def test_vidriera_rules_warnings_and_identity(client: TestClient, engine) -> None:
    quinta_id = _quinta_id(client)
    vidriera = _vidriera(client, quinta_id, "VE-V001", "Norte")
    vidriera_id = vidriera["id"]
    assert len(vidriera["canteros"]) == 4

    unmapped = client.get(f"/api/production/vidrieras/{vidriera_id}/boundary")
    assert unmapped.status_code == 200
    assert unmapped.json()["geometry"] is None

    without_quinta = client.put(
        f"/api/production/vidrieras/{vidriera_id}/boundary",
        json={"geometry": _polygon(INSIDE), "mode": "attach"},
    )
    assert without_quinta.status_code == 409
    assert "límite de la quinta" in without_quinta.json()["detail"]
    assert (
        client.get(f"/api/production/vidrieras/{vidriera_id}/boundary").json()[
            "geometry"
        ]
        is None
    )

    client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(QUINTA)},
    )
    client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(TRIANGLE), "mode": "replace"},
    )
    bbox_only = client.put(
        f"/api/production/vidrieras/{vidriera_id}/boundary",
        json={"geometry": _polygon(OUTSIDE_BBOX)},
    )
    assert bbox_only.status_code == 422
    assert "no intersecta" in bbox_only.json()["detail"]

    client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(QUINTA), "mode": "replace"},
    )
    disconnected = client.put(
        f"/api/production/vidrieras/{vidriera_id}/boundary",
        json={"geometry": _polygon(DISCONNECTED), "mode": "attach"},
    )
    assert disconnected.status_code == 422
    large = client.put(
        f"/api/production/vidrieras/{vidriera_id}/boundary",
        json={"geometry": _polygon(LARGE_OVERFLOW), "mode": "attach"},
    )
    assert large.status_code == 422
    assert "considerable" in large.json()["detail"]
    assert (
        client.get(f"/api/production/vidrieras/{vidriera_id}/boundary").json()[
            "geometry"
        ]
        is None
    )

    saved = client.put(
        f"/api/production/vidrieras/{vidriera_id}/boundary",
        json={"geometry": _polygon(MINOR_OVERFLOW), "mode": "attach"},
    )
    assert saved.status_code == 200
    assert saved.json()["geometry"]["coordinates"] == [MINOR_OVERFLOW]
    assert saved.json()["warnings"][0]["code"] == "boundary_overflow"
    assert "un poco" in saved.json()["warnings"][0]["message"]

    second = _vidriera(client, quinta_id, "VE-V002", "Sur")
    overlap = client.put(
        f"/api/production/vidrieras/{second['id']}/boundary",
        json={"geometry": _polygon(OVERLAP), "mode": "attach"},
    )
    assert overlap.status_code == 200
    assert overlap.json()["warnings"][0]["code"] == "vidriera_overlap"
    assert overlap.json()["warnings"][0]["vidriera_code"] == "VE-V001"
    assert overlap.json()["geometry"]["coordinates"] == [OVERLAP]

    blocked = client.put(
        f"/api/production/vidrieras/{second['id']}/boundary",
        json={"geometry": _polygon(INSIDE), "mode": "attach"},
    )
    assert blocked.status_code == 409
    assert "ya tiene un límite" in blocked.json()["detail"]
    assert client.get(f"/api/production/vidrieras/{second['id']}/boundary").json()[
        "geometry"
    ]["coordinates"] == [OVERLAP]

    detail = client.get(f"/api/production/vidrieras/{vidriera_id}").json()
    assert detail["id"] == vidriera_id
    assert detail["code"] == "VE-V001"
    assert [cantero["number"] for cantero in detail["canteros"]] == [1, 2, 3, 4]
    assert _counts(engine) == {"quintas": 1, "vidrieras": 2, "canteros": 8}

    removed = client.delete(f"/api/production/vidrieras/{vidriera_id}/boundary")
    assert removed.status_code == 204
    assert (
        client.get(f"/api/production/vidrieras/{vidriera_id}/boundary").json()[
            "geometry"
        ]
        is None
    )
    assert client.get(f"/api/production/vidrieras/{vidriera_id}").json()["code"] == (
        "VE-V001"
    )


def test_map_lists_mapped_and_unmapped_vidrieras(client: TestClient) -> None:
    quinta_id = _quinta_id(client)
    first = _vidriera(client, quinta_id, "VE-V001", "Norte")
    second = _vidriera(client, quinta_id, "VE-V002", "Sur")
    client.put(
        f"/api/production/quintas/{quinta_id}/boundary",
        json={"geometry": _polygon(QUINTA)},
    )
    client.put(
        f"/api/production/vidrieras/{first['id']}/boundary",
        json={"geometry": _polygon(INSIDE)},
    )
    client.patch(
        f"/api/production/vidrieras/{second['id']}",
        json={"active": False},
    )

    visible = client.get(f"/api/production/quintas/{quinta_id}/map").json()
    assert visible["geometry"]["type"] == "Polygon"
    assert [item["code"] for item in visible["vidrieras"]] == ["VE-V001"]
    assert visible["vidrieras"][0]["geometry"]["coordinates"] == [INSIDE]

    everyone = client.get(
        f"/api/production/quintas/{quinta_id}/map?include_inactive=true"
    ).json()
    by_code = {item["code"]: item for item in everyone["vidrieras"]}
    assert by_code["VE-V002"]["geometry"] is None
    assert by_code["VE-V002"]["active"] is False


def test_upgrade_preserves_records_and_downgrade_drops_only_geometry() -> None:
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    config = _alembic_config()
    quinta_id = uuid.uuid4()
    vidriera_id = uuid.uuid4()
    try:
        command.upgrade(config, "0001_production_hierarchy")
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
        connected.dispose()

        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.connect() as connection:
            boundary = connection.scalar(
                text("SELECT boundary FROM quintas WHERE id = :id"),
                {"id": quinta_id},
            )
            vidriera_boundary = connection.scalar(
                text("SELECT boundary FROM vidrieras WHERE id = :id"),
                {"id": vidriera_id},
            )
        assert boundary is None
        assert vidriera_boundary is None
        with connected.begin() as connection:
            connection.execute(
                text("UPDATE quintas SET boundary = CAST(:boundary AS jsonb)"),
                {"boundary": '{"type":"Polygon","coordinates":[]}'},
            )
        connected.dispose()

        command.downgrade(config, "0001_production_hierarchy")
        connected = create_engine(url)
        with connected.connect() as connection:
            columns = set(
                connection.scalars(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'quintas'"
                    )
                )
            )
            code = connection.scalar(
                text("SELECT code FROM quintas WHERE id = :id"),
                {"id": quinta_id},
            )
            vidriera_code = connection.scalar(
                text("SELECT code FROM vidrieras WHERE id = :id"),
                {"id": vidriera_id},
            )
        connected.dispose()
        assert "boundary" not in columns
        assert code == "VE"
        assert vidriera_code == "VE-V001"

        command.upgrade(config, "head")
        connected = create_engine(url)
        with connected.connect() as connection:
            restored = connection.scalar(
                text("SELECT boundary FROM quintas WHERE id = :id"),
                {"id": quinta_id},
            )
        connected.dispose()
        assert restored is None
    finally:
        restore_alembic_url(previous)
        drop_isolated_database(name)


def test_boundary_route_reports_missing_column_as_schema_not_applied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ACCESS_SECRET", "")
    name, url = create_isolated_database()
    previous = use_alembic_url(url)
    try:
        command.upgrade(_alembic_config(), "0001_production_hierarchy")
        connected = create_engine(url, pool_pre_ping=True)
        sessions = sessionmaker(bind=connected, autoflush=False, expire_on_commit=False)

        def override_session():
            session = sessions()
            try:
                yield session
            finally:
                session.close()

        get_settings.cache_clear()
        application = create_app()
        application.dependency_overrides[get_db_session] = override_session
        with TestClient(application, raise_server_exceptions=False) as test_client:
            response = test_client.get(
                f"/api/production/quintas/{uuid.uuid4()}/boundary"
            )
        connected.dispose()
    finally:
        get_settings.cache_clear()
        restore_alembic_url(previous)
        drop_isolated_database(name)

    assert response.status_code == 503
    assert response.json()["detail"] == SCHEMA_NOT_APPLIED_DETAIL
    assert "boundary" not in response.text


def _polygon(ring: list[list[float]]) -> dict:
    return {"type": "Polygon", "coordinates": [ring]}


def _quinta_id(client: TestClient) -> str:
    response = client.post(
        "/api/production/quintas",
        json={"code": "VE", "name": "Villa Elisa"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _vidriera(client: TestClient, quinta_id: str, code: str, name: str) -> dict:
    response = client.post(
        f"/api/production/quintas/{quinta_id}/vidrieras",
        json={"code": code, "name": name},
    )
    assert response.status_code == 201
    return response.json()


def _counts(engine) -> dict[str, int]:
    with engine.connect() as connection:
        return {
            table: connection.scalar(text(f"SELECT count(*) FROM {table}"))
            for table in ("quintas", "vidrieras", "canteros")
        }


def _alembic_config() -> Config:
    return Config(f"{BACKEND_ROOT}/alembic.ini")
