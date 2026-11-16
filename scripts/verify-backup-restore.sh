#!/usr/bin/env bash
# Round-trip a probe row through pg_dump and pg_restore.
# Creates two uniquely named databases and drops only those this run created.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=db-safety.sh
source "${ROOT}/scripts/db-safety.sh"

PRIMARY=$(resolve_primary_database "$ROOT")
NOTE="core-01 isolated backup probe"
DUMP=""

cleanup() {
  local status=$?
  trap - EXIT INT TERM
  set +e
  drop_owned_databases "$PRIMARY"
  if [[ -n "$DUMP" ]]; then
    rm -f "$DUMP"
  fi
  exit "$status"
}
trap cleanup EXIT INT TERM

psql_exec() {
  local database=$1
  local sql=$2
  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname="$1" -v ON_ERROR_STOP=1 -c "$2"' \
    sh "$database" "$sql"
}

SRC=$(allocate_probe_database src "$PRIMARY")
psql_exec postgres "CREATE DATABASE \"${SRC}\""
remember_created_database "$SRC" "$PRIMARY"

psql_exec "$SRC" "CREATE TABLE core01_backup_probe (id integer PRIMARY KEY, note text NOT NULL)"
psql_exec "$SRC" "INSERT INTO core01_backup_probe (id, note) VALUES (1, '${NOTE}')"

mkdir -p "${ROOT}/backups"
DUMP=$(mktemp "${ROOT}/backups/core01-probe.XXXXXX")
bash "${ROOT}/scripts/db-backup.sh" "$SRC" "$DUMP"

DST=$(allocate_probe_database dst "$PRIMARY")
bash "${ROOT}/scripts/db-restore.sh" "$DUMP" "$DST"
remember_created_database "$DST" "$PRIMARY"

READ_BACK="$(
  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname="$1" -v ON_ERROR_STOP=1 -tAc "SELECT note FROM core01_backup_probe WHERE id = 1"' \
    sh "$DST"
)"
READ_BACK="$(printf '%s' "$READ_BACK" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

if [[ "$READ_BACK" != "$NOTE" ]]; then
  echo "restored note does not match: ${READ_BACK}" >&2
  exit 1
fi

PRIMARY_PROBE="$(
  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname="$1" -tAc "SELECT to_regclass('\''public.core01_backup_probe'\'')"' \
    sh "$PRIMARY"
)"
PRIMARY_PROBE="${PRIMARY_PROBE//[[:space:]]/}"

if [[ -n "$PRIMARY_PROBE" ]]; then
  echo "probe table appeared in the primary database" >&2
  exit 1
fi

echo "backup restore verified for ${NOTE}"
