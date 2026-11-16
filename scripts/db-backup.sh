#!/usr/bin/env bash
# Dump one PostgreSQL database from the Compose db service.
# Usage: scripts/db-backup.sh <database-name> <output-file>
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: scripts/db-backup.sh <database-name> <output-file>" >&2
  exit 2
fi

DATABASE_NAME=$1
OUTPUT_FILE=$2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$OUTPUT_FILE" != /* ]]; then
  OUTPUT_FILE="$(pwd)/${OUTPUT_FILE}"
fi

if [[ ! "$DATABASE_NAME" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "refusing database name: ${DATABASE_NAME}" >&2
  exit 1
fi

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT_FILE")"

docker compose exec -T db \
  sh -c 'pg_dump --format=custom --no-owner --no-acl --username="$POSTGRES_USER" --dbname="$1"' \
  sh "$DATABASE_NAME" >"$OUTPUT_FILE"

if [[ ! -s "$OUTPUT_FILE" ]]; then
  echo "backup file is empty: ${OUTPUT_FILE}" >&2
  exit 1
fi
