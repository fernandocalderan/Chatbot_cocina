# Subflows v2 Baseline (pre-sequential)

Este documento congela el contrato y las piezas existentes antes de añadir el modo **sequential**.

## Archivos y piezas clave (estado actual)
- Runtime / resolver:
  - `backend/app/services/flow_resolver.py` → resuelve flow runtime (v1/v2) usado por chat/widget.
  - `backend/app/api/chat.py` → handoff router → subflow (v1-safe).
  - `backend/app/api/widget.py` → runtime config para widget.
- Subflows + overrides:
  - `backend/app/services/subflow_overrides.py` → overrides seguros (solo `text` y `options[].label`).
  - `backend/app/api/tenant_flows_v2.py` → endpoints `/v1/tenant/flows/*`.
  - `backend/app/services/verticals.py` → utilidades: `build_vertical_subflow_filename`, `vertical_list_subflows`, `vertical_read_asset_json`.
- Panel tenant:
  - `panel/pages/flujo_v2.py` → editor v2 (draft/publish + subflow editor básico).
  - `panel/api_client.py` → calls `/tenant/flows/subflows`.
- Panel admin:
  - `admin_panel/pages/03_🧩_Verticals.py` → scaffolding de subflows + edición de archivos de vertical.
  - `admin_panel/api_client.py` → calls `/v1/admin/verticals/*`.

## Contrato actual (compatibilidad)
### GET `/v1/tenant/flows/subflows`
Devuelve catálogo de subflows (router-based). Payload actual:
```
{
  "tenant_id": "uuid",
  "router": {
    "block_id": "string",
    "save_to": "string",
    "routes_file": "string"
  },
  "subflows": [
    {
      "key": "string",
      "label": "string",
      "file": "subflow_scope_*__*__*.json",
      "subflow_id": "string|null",
      "has_overrides": true|false
    }
  ]
}
```

### GET `/v1/tenant/flows/subflows/{subflow_key}`
Devuelve base + effective (con overrides aplicados):
```
{
  "tenant_id": "uuid",
  "key": "string",
  "subflow_id": "string|null",
  "file": "subflow_scope_*__*__*.json",
  "base": { ...flow... },
  "effective": { ...flow... },
  "has_overrides": true|false
}
```

### PATCH `/v1/tenant/flows/subflows/{subflow_key}/blocks/{block_id}`
Permite overrides seguros:
- `text` (multi-idioma)
- `options[].label` (multi-idioma)

## Roles actuales
- Tenant: `OWNER` / `ADMIN` (via `require_any_role` en `/tenant/flows/*`).
- Admin: SuperAdmin (via `/v1/admin/*`).

## Checks manuales (baseline)
- `GET /v1/tenant/flows/subflows` devuelve catálogo basado en router.
- `PATCH /v1/tenant/flows/subflows/{key}/blocks/{id}` aplica overrides solo a copy.
