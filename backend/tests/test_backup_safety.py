import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SAFETY_LIB = REPO_ROOT / "scripts" / "db-safety.sh"


def run_bash(
    script: str,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", script],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )


def test_cleanup_drops_only_databases_created_by_this_run() -> None:
    result = run_bash(
        f"""
        source "{SAFETY_LIB}"
        drop_created_database() {{ printf 'drop %s\\n' "$1"; }}
        remember_created_database created_by_this_run monteiro
        remember_created_database second_created_db monteiro
        drop_owned_databases monteiro
        """
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "drop created_by_this_run",
        "drop second_created_db",
    ]


def test_cleanup_refuses_to_track_the_primary_database() -> None:
    result = run_bash(
        f"""
        source "{SAFETY_LIB}"
        if remember_created_database monteiro monteiro; then
          printf 'tracked\\n'
        else
          printf 'refused\\n'
        fi
        drop_created_database() {{ printf 'drop %s\\n' "$1"; }}
        drop_owned_databases monteiro
        """
    )

    assert result.returncode == 0
    assert result.stdout == "refused\n"


def test_name_collision_keeps_the_existing_database_and_chooses_another() -> None:
    result = run_bash(
        f"""
        source "{SAFETY_LIB}"
        database_exists() {{ [[ "$1" == "core01_probe_src_taken" ]]; }}
        name=$(select_unused_name monteiro core01_probe_src_taken core01_probe_src_free)
        printf '%s' "$name"
        """
    )

    assert result.returncode == 0
    assert result.stdout == "core01_probe_src_free"
    assert "leaving it untouched" in result.stderr
    assert "DROP" not in result.stderr


def test_name_collision_fails_when_every_candidate_exists() -> None:
    result = run_bash(
        f"""
        set -euo pipefail
        source "{SAFETY_LIB}"
        database_exists() {{ return 0; }}
        if name=$(select_unused_name monteiro \
          core01_probe_src_taken core01_probe_dst_taken); then
          printf 'selected %s\\n' "$name"
          exit 1
        fi
        printf 'unallocated\\n'
        """
    )

    assert result.returncode == 0
    assert result.stdout == "unallocated\n"
    assert "could not allocate" in result.stderr


def test_allocator_skips_protected_names() -> None:
    result = run_bash(
        f"""
        source "{SAFETY_LIB}"
        database_exists() {{ return 1; }}
        name=$(select_unused_name monteiro monteiro postgres \
          template0 template1 core01_probe_src_ok)
        printf '%s' "$name"
        """
    )

    assert result.returncode == 0
    assert result.stdout == "core01_probe_src_ok"


def test_primary_name_prefers_the_environment_over_dotenv(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("POSTGRES_DB=from_file\n")
    env = os.environ.copy()
    env["POSTGRES_DB"] = "from_env"
    result = run_bash(
        f'source "{SAFETY_LIB}"\nresolve_primary_database "{tmp_path}"\n',
        env=env,
    )

    assert result.returncode == 0
    assert result.stdout == "from_env"


def test_primary_name_reads_dotenv_when_the_environment_is_unset(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env").write_text('export POSTGRES_DB="quoted_db"\n')
    env = os.environ.copy()
    env.pop("POSTGRES_DB", None)
    result = run_bash(
        f'source "{SAFETY_LIB}"\nresolve_primary_database "{tmp_path}"\n',
        env=env,
    )

    assert result.returncode == 0
    assert result.stdout == "quoted_db"


def test_primary_name_defaults_like_compose(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("POSTGRES_DB", None)
    result = run_bash(
        f'source "{SAFETY_LIB}"\nresolve_primary_database "{tmp_path}"\n',
        env=env,
    )

    assert result.returncode == 0
    assert result.stdout == "monteiro"
