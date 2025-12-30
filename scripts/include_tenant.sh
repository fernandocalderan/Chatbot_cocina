#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

API_BASE="${API_BASE:-http://localhost:8100}"
TENANT_ID="${1:-}"
REASON="${2:-}"

if [[ -z "${TENANT_ID}" ]]; then
  echo "Usage: $0 <tenant_id> [reason]" >&2
  exit 2
fi

ADMIN_TOKEN="${ADMIN_API_TOKEN:-${ADMIN_API_KEY:-}}"
if [[ -z "${ADMIN_TOKEN}" && -f "${ROOT_DIR}/backend/.env" ]]; then
  ADMIN_TOKEN="$(rg -n \"^(ADMIN_API_TOKEN|ADMIN_API_KEY)=\" -m 1 \"${ROOT_DIR}/backend/.env\" | sed -E 's/^([^=]+)=//')"
fi
if [[ -z "${ADMIN_TOKEN}" ]]; then
  echo "Missing ADMIN_API_TOKEN/ADMIN_API_KEY (set env or backend/.env)" >&2
  exit 2
fi

payload="{}"
if [[ -n "${REASON}" ]]; then
  payload="$(jq -n --arg reason "${REASON}" '{reason:$reason}')"
fi

curl -sS -H "x-api-key: ${ADMIN_TOKEN}" -H "Content-Type: application/json" \
  -d "${payload}" \
  "${API_BASE%/}/v1/admin/tenants/${TENANT_ID}/include" | jq .

