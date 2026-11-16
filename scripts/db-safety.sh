#!/usr/bin/env bash
# Shared checks for backup scripts. Safe to source; it does not create or drop databases.
# Docker Compose resolves POSTGRES_DB from the shell, then the repo .env, then "monteiro".

OWNED_DATABASES=()

resolve_primary_database() {
  local root=$1
  local env_file value line

  if [[ -n "${POSTGRES_DB:-}" ]]; then
    printf '%s' "$POSTGRES_DB"
    return 0
  fi

  env_file="${root}/.env"
  if [[ -f "$env_file" ]]; then
    line=$(grep -E '^[[:space:]]*(export[[:space:]]+)?POSTGRES_DB=' "$env_file" | tail -n 1 || true)
    if [[ -n "$line" ]]; then
      value=${line#*=}
      value=${value%%#*}
      value=$(printf '%s' "$value" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
      if [[ -n "$value" ]]; then
        printf '%s' "$value"
        return 0
      fi
    fi
  fi

  printf '%s' monteiro
}

identifier_is_safe() {
  local name=$1
  local primary=$2

  [[ "$name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || return 1
  [[ ${#name} -le 63 ]] || return 1
  [[ "$name" != "$primary" ]] || return 1
  [[ "$name" != "postgres" && "$name" != "template0" && "$name" != "template1" ]] || return 1
  return 0
}

random_token() {
  if [[ -r /proc/sys/kernel/random/uuid ]]; then
    tr -d '-' </proc/sys/kernel/random/uuid | cut -c 1-12
    return 0
  fi
  od -An -N6 -tx1 /dev/urandom | tr -d ' \n'
}

new_probe_identifier() {
  local role=$1
  printf 'core01_probe_%s_%s_%s' "$role" "$$" "$(random_token)"
}

database_exists() {
  local name=$1
  local found

  found=$(
    docker compose exec -T db \
      sh -c 'psql --username="$POSTGRES_USER" --dbname=postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '\''$1'\''"' \
      sh "$name"
  )
  found=${found//[[:space:]]/}
  [[ "$found" == "1" ]]
}

select_unused_name() {
  local primary=$1
  shift
  local name

  for name in "$@"; do
    identifier_is_safe "$name" "$primary" || continue
    if database_exists "$name"; then
      echo "database ${name} already exists; leaving it untouched" >&2
      continue
    fi
    printf '%s' "$name"
    return 0
  done

  echo "could not allocate an unused database name" >&2
  return 1
}

allocate_probe_database() {
  local role=$1
  local primary=$2
  local names=()
  local attempt

  for attempt in 1 2 3 4 5 6 7 8; do
    names+=("$(new_probe_identifier "$role")")
  done
  select_unused_name "$primary" "${names[@]}"
}

remember_created_database() {
  local name=$1
  local primary=$2

  if ! identifier_is_safe "$name" "$primary"; then
    echo "refusing to track ${name} for cleanup" >&2
    return 1
  fi
  OWNED_DATABASES+=("$name")
}

drop_created_database() {
  local name=$1
  local primary=$2

  if ! identifier_is_safe "$name" "$primary"; then
    echo "refusing to drop ${name}" >&2
    return 1
  fi

  docker compose exec -T db \
    sh -c 'psql --username="$POSTGRES_USER" --dbname=postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"$1\" WITH (FORCE)"' \
    sh "$name" >/dev/null
}

drop_owned_databases() {
  local primary=$1
  local name

  if [[ ${#OWNED_DATABASES[@]} -eq 0 ]]; then
    return 0
  fi
  for name in "${OWNED_DATABASES[@]}"; do
    drop_created_database "$name" "$primary" || echo "warning: could not drop ${name}; leaving it for inspection" >&2
  done
  OWNED_DATABASES=()
}
