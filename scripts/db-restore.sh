#!/usr/bin/env bash
# Restore a custom-format dump into a separate empty database.
# Refuses the primary application database and PostgreSQL maintenance databases.
# Usage: scripts/db-restore.sh <backup-file> <target-database>
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: scripts/db-restore.sh <backup-file> <target-database>" >&2
  exit 2
fi

BACKUP_FILE=$1
TARGET=$2
PRIMARY=${POSTGRES_DB:-monteiro}
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$BACKUP_FILE" != /* ]]; then
  BACKUP_FILE="$(pwd)/${BACKUP_FILE}"
fi

if [[ ! "$TARGET" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "refusing target database name: ${TARGET}" >&2
  exit 1
fi

if [[ "$TARGET" == "$PRIMARY" || "$TARGET" == "postgres" || "$TARGET" == "template0" || "$TARGET" == "template1" ]]; then
  echo "refusing to restore into ${TARGET}; choose a separate empty database" >&2
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

cd "$ROOT"

EXISTS="$(
  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname=postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '\''$1'\''"' \
    sh "$TARGET"
)"
EXISTS="${EXISTS//[[:space:]]/}"

if [[ "$EXISTS" == "1" ]]; then
  echo "refusing to restore into existing database ${TARGET}" >&2
  exit 1
fi

docker compose exec -T db \
  sh -c 'psql --username="$POSTGRES_USER" --dbname=postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$1\""' \
  sh "$TARGET"

docker compose exec -T db \
  sh -c 'pg_restore --no-owner --no-acl --exit-on-error --username="$POSTGRES_USER" --dbname="$1"' \
  sh "$TARGET" <"$BACKUP_FILE"
