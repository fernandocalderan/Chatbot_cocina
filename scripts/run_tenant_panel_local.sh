#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PORT="${PORT:-8501}"
HOST="${HOST:-0.0.0.0}"

exec "${ROOT_DIR}/panel/.venv/bin/streamlit" run \
  "${ROOT_DIR}/panel/app.py" \
  --server.address "${HOST}" \
  --server.port "${PORT}"

