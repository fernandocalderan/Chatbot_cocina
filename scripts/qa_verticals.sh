#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

STRICT_FLAG=""
if [[ "${1:-}" == "--strict" ]]; then
  STRICT_FLAG="--strict"
fi

python3 "$ROOT/backend/app/scripts/validate_verticals.py" $STRICT_FLAG
