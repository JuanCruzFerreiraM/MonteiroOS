import os
import subprocess
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-backup-restore.sh"
RESTORE_SCRIPT = REPO_ROOT / "scripts" / "db-restore.sh"
SAFETY_LIB = REPO_ROOT / "scripts" / "db-safety.sh"


def _run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )


def _psql(database: str, sql: str) -> subprocess.CompletedProcess[str]:
    return _run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "db",
            "sh",
            "-c",
            "psql --username=\"$POSTGRES_USER\" --dbname=\"$1\" "
            '-v ON_ERROR_STOP=1 -tAc "$2"',
            "sh",
            database,
            sql,
        ]
    )


def _compose_database_ready() -> bool:
    result = _run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "db",
            "sh",
            "-c",
            'pg_isready -U "$POSTGRES_USER" -d postgres',
        ]
    )
    return result.returncode == 0


def _primary_database() -> str:
    env = os.environ.copy()
    env.pop("POSTGRES_DB", None)
    script = f'source "{SAFETY_LIB}"\nresolve_primary_database "{REPO_ROOT}"\n'
    result = _run(["bash", "-c", script], env=env)
    assert result.returncode == 0
    return result.stdout.strip()


def _probe_databases() -> set[str]:
    result = _psql(
        "postgres",
        "SELECT datname FROM pg_database "
        "WHERE datname LIKE 'core01_probe_%' ORDER BY 1",
    )
    assert result.returncode == 0
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _public_table_count(database: str) -> str:
    result = _psql(
        database,
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = 'public'",
    )
    assert result.returncode == 0
    return result.stdout.strip()


@pytest.fixture
def compose_database() -> None:
    if not _compose_database_ready():
        pytest.skip("Compose PostgreSQL is not available")


def _drop_known_database(name: str) -> None:
    result = _psql(
        "postgres",
        f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)',
    )
    assert result.returncode == 0


def test_round_trip_preserves_a_preexisting_probe_like_database(
    compose_database: None,
) -> None:
    primary = _primary_database()
    keep_name = f"core01_probe_src_keep_{uuid.uuid4().hex[:8]}"
    before = _probe_databases()
    primary_tables = _public_table_count(primary)
    created = False

    try:
        created_db = _psql("postgres", f'CREATE DATABASE "{keep_name}"')
        assert created_db.returncode == 0
        created = True
        marker = _psql(
            keep_name,
            "CREATE TABLE keep_marker (id integer PRIMARY KEY);"
            " INSERT INTO keep_marker (id) VALUES (7);",
        )
        assert marker.returncode == 0

        verified = _run(["bash", str(VERIFY_SCRIPT)])
        assert verified.returncode == 0, verified.stderr
        assert "backup restore verified" in verified.stdout

        marker_value = _psql(keep_name, "SELECT id FROM keep_marker")
        assert marker_value.returncode == 0
        assert marker_value.stdout.strip() == "7"
        assert _probe_databases() - {keep_name} == before
        assert _public_table_count(primary) == primary_tables
    finally:
        if created:
            _drop_known_database(keep_name)


def test_restore_refuses_an_existing_target_without_changing_it(
    compose_database: None,
) -> None:
    target = f"core01_restore_keep_{uuid.uuid4().hex[:8]}"
    created = False
    try:
        created_db = _psql("postgres", f'CREATE DATABASE "{target}"')
        assert created_db.returncode == 0
        created = True
        marker = _psql(
            target,
            "CREATE TABLE keep_marker (id integer PRIMARY KEY);"
            " INSERT INTO keep_marker (id) VALUES (3);",
        )
        assert marker.returncode == 0

        dummy = REPO_ROOT / "backups" / f"not-a-real-dump-{target}"
        dummy.parent.mkdir(exist_ok=True)
        dummy.write_text("not a dump\n")
        try:
            refused = _run(["bash", str(RESTORE_SCRIPT), str(dummy), target])
        finally:
            dummy.unlink(missing_ok=True)

        assert refused.returncode == 1
        assert "refusing to restore into existing database" in refused.stderr
        marker_value = _psql(target, "SELECT id FROM keep_marker")
        assert marker_value.stdout.strip() == "3"
    finally:
        if created:
            _drop_known_database(target)


def test_round_trip_with_a_non_default_primary_name(compose_database: None) -> None:
    alt_name = f"core01_alt_primary_{uuid.uuid4().hex[:8]}"
    created = False
    env = os.environ.copy()
    env["POSTGRES_DB"] = alt_name
    try:
        created_db = _psql("postgres", f'CREATE DATABASE "{alt_name}"')
        assert created_db.returncode == 0
        created = True
        marker = _psql(
            alt_name,
            "CREATE TABLE keep_marker (id integer PRIMARY KEY);"
            " INSERT INTO keep_marker (id) VALUES (11);",
        )
        assert marker.returncode == 0
        monteiro_exists = (
            _psql(
                "postgres",
                "SELECT 1 FROM pg_database WHERE datname = 'monteiro'",
            ).stdout.strip()
            == "1"
        )
        default_tables = _public_table_count("monteiro") if monteiro_exists else None

        verified = _run(["bash", str(VERIFY_SCRIPT)], env=env)
        assert verified.returncode == 0, verified.stderr

        marker_value = _psql(alt_name, "SELECT id FROM keep_marker")
        assert marker_value.stdout.strip() == "11"
        probe = _psql(alt_name, "SELECT to_regclass('public.core01_backup_probe')")
        assert probe.stdout.strip() == ""
        if monteiro_exists:
            assert _public_table_count("monteiro") == default_tables
    finally:
        if created:
            _drop_known_database(alt_name)
