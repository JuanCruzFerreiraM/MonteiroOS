import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def protected_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ACCESS_SECRET", "test-secret")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            yield client
    finally:
        get_settings.cache_clear()


def test_health_stays_public_when_secret_is_set(protected_client: TestClient) -> None:
    response = protected_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_secret_rejects_requests_without_the_header(
    protected_client: TestClient,
) -> None:
    response = protected_client.get("/production/quintas")

    assert response.status_code == 401
    assert response.json() == {"detail": "access denied"}


def test_secret_rejects_a_wrong_header(protected_client: TestClient) -> None:
    response = protected_client.get(
        "/openapi.json",
        headers={"X-Monteiro-Access": "wrong-secret"},
    )

    assert response.status_code == 401


def test_secret_allows_the_matching_header(protected_client: TestClient) -> None:
    denied = protected_client.get("/production/quintas")
    allowed = protected_client.get(
        "/production/quintas",
        headers={"X-Monteiro-Access": "test-secret"},
    )

    assert denied.status_code == 401
    assert allowed.status_code == 404


def test_blank_secret_does_not_lock_the_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ACCESS_SECRET", "   ")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            response = client.get("/openapi.json")
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
