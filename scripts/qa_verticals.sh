#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/backend/app/scripts/validate_verticals.py" "$@"
