#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

API_PORT="${API_PORT:-8100}"
API_HOST="${API_HOST:-0.0.0.0}"

# Cuando ejecutas uvicorn fuera de docker, `backend/.env` apunta a `db`/`redis`.
# Override seguro para usar los puertos mapeados por docker-compose.
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://postgres:postgres@localhost:5433/chatbot}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6382/0}"

exec "${ROOT_DIR}/backend/.venv/bin/uvicorn" \
  app.main:app \
  --app-dir "${ROOT_DIR}/backend" \
  --reload \
  --host "${API_HOST}" \
  --port "${API_PORT}"

