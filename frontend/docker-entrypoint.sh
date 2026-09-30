#!/bin/sh
set -eu

lock_hash="$(sha256sum package-lock.json | awk '{print $1}')"
stamp="node_modules/.lock-hash"

if [ ! -f "$stamp" ] || [ "$(cat "$stamp")" != "$lock_hash" ]; then
  npm ci
  echo "$lock_hash" > "$stamp"
fi

exec npm run dev -- --hostname 0.0.0.0 --port 3000
