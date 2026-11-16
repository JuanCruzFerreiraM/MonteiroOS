#!/usr/bin/env bash
# Round-trip a probe row through pg_dump and pg_restore.
# Uses two throwaway databases and never writes the probe into the primary database.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PRIMARY=${POSTGRES_DB:-monteiro}
SRC=monteiro_backup_probe_src
DST=monteiro_backup_probe_dst
DUMP="${ROOT}/backups/core01-probe.dump"
NOTE="core-01 isolated backup probe"

if [[ "$SRC" == "$PRIMARY" || "$DST" == "$PRIMARY" ]]; then
  echo "probe database names collide with the primary database" >&2
  exit 1
fi

psql_exec() {
  local database=$1
  local sql=$2
  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname="$1" -v ON_ERROR_STOP=1 -c "$2"' \
    sh "$database" "$sql"
}

drop_probe() {
  local name=$1
  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname=postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"$1\" WITH (FORCE)"' \
    sh "$name" >/dev/null
}

cleanup() {
  drop_probe "$SRC" || true
  drop_probe "$DST" || true
  rm -f "$DUMP"
}

trap cleanup EXIT

drop_probe "$SRC"
drop_probe "$DST"

psql_exec postgres "CREATE DATABASE ${SRC}"
psql_exec "$SRC" "CREATE TABLE core01_backup_probe (id integer PRIMARY KEY, note text NOT NULL)"
psql_exec "$SRC" "INSERT INTO core01_backup_probe (id, note) VALUES (1, '${NOTE}')"

mkdir -p "${ROOT}/backups"
bash "${ROOT}/scripts/db-backup.sh" "$SRC" "$DUMP"
bash "${ROOT}/scripts/db-restore.sh" "$DUMP" "$DST"

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
