#!/bin/sh
set -eu

uv sync --frozen
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
