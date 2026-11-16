import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
RESTORE_SCRIPT = REPO_ROOT / "scripts" / "db-restore.sh"


def test_compose_publishes_services_on_loopback() -> None:
    text = COMPOSE_FILE.read_text()

    assert '127.0.0.1:${POSTGRES_PORT:-5432}:5432' in text
    assert '127.0.0.1:${BACKEND_PORT:-8000}:8000' in text
    assert '127.0.0.1:${FRONTEND_PORT:-3000}:3000' in text


def test_restore_refuses_the_primary_database() -> None:
    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT), "missing.dump", "monteiro"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={"POSTGRES_DB": "monteiro", "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 1
    assert "refusing to restore" in result.stderr


def test_restore_refuses_the_maintenance_database() -> None:
    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT), "missing.dump", "postgres"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={"POSTGRES_DB": "monteiro", "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 1
    assert "refusing to restore" in result.stderr
