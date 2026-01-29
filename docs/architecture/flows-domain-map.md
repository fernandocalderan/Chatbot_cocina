# Flow Domain Map (Verticals / Scopes / Flows / Subflows)

## Resumen
El dominio actual mezcla **plantillas en filesystem** (verticals/scopes/subflows) con **flows versionados en DB** por tenant. El runtime resuelve **solo flows publicados** y usa las plantillas del vertical para base/legacy.

## Source of Truth actual
- **Filesystem (plantillas globales)**: `backend/app/verticals/<vertical_key>/...`
- **DB (flows publicados por tenant)**: tabla `flows`
- **Overrides / materiales tenant**: `configs` (tipo `tenant_flow_materials`, `tenant_subflow_overrides`, etc.)

## Tablas y relaciones (SQLAlchemy)
### `tenants`
- PK: `tenants.id` (UUID)
- Campos relevantes:
  - `vertical_key` (string) → vertical asignado
  - `flow_mode` ("LEGACY" | "VERTICAL")
  - `active_flow_id` (UUID, soft pointer)
  - `branding` (JSONB) → `vertical_scopes` (lista de scopes)
- Relación:
  - 1 tenant → many `flows`

### `flows`
- PK: `flows.id` (UUID)
- FK: `tenant_id` → `tenants.id`
- Campos:
  - `version` (int)
  - `estado` ("draft" | "published")
  - `published_at`
  - `schema_json` (JSONB)
  - `vertical_key` (string, opcional)
- Constraint:
  - `uq_flow_version_per_tenant` (tenant_id + version)

### `configs`
- PK: `configs.id` (UUID)
- FK: `tenant_id` → `tenants.id`
- Campos:
  - `tipo` (string)
  - `payload_json` (JSONB)
  - `version` (int)
- Tipos relevantes:
  - `tenant_flow_materials`
  - `tenant_subflow_overrides`
  - `tenant_semantic_schema`
  - `tenant_kpi_defaults`

### `conversation_templates`
- PK: `conversation_templates.id` (UUID)
- FK: `tenant_id` (nullable)
- Campos:
  - `schema_json` (plantilla conversacional legacy)
  - `is_default`
- Nota: coexistencia legacy con `flows` versionados.

## Filesystem (plantillas globales)
Raíz: `backend/app/verticals/`

- `registry.json`: catálogo de verticales (metadatos visibles en panel)
- `<vertical_key>/metadata.json`: config de vertical y scopes
- `<vertical_key>/flow_base.json`: flow base global del vertical
- `<vertical_key>/flow_base_scope_<scope>.json`: flow base por scope (legacy)
- `<vertical_key>/subflow_scope_<scope>__<group>__<key>.json`: subflows legacy
- `<vertical_key>/subflows/<scope>/<group>/<key>.json`: subflows V2
- `prompt_vertical*.txt` / `prompt_scope_*.txt`: prompts

## Relaciones “conceptuales”
```
Vertical (filesystem) → Scopes (metadata.json)
Scope → Flow base (flow_base_scope_<scope>.json)
Scope → Subflows (legacy o V2)
Tenant → Flow publicado (DB) → runtime
Tenant → overrides (configs)
```

## Estados esperados por Scope (catálogo)
- `NO_FLOW_YET`: scope sin flow base ni subflows
- `DRAFT_ONLY`: scope con flow base pero sin subflows
- `PUBLISHED_OK`: el tenant tiene flow publicado para ese vertical
- `MULTIPLE_PUBLISHED`: inconsistencia en DB (más de un published)

## Observaciones clave
- El runtime usa **solo published** de DB para tenant (resolver estricto).
- Los scopes viven en **filesystem**, no hay tabla `scopes` en DB.
- El panel debe listar **scopes vacíos** (no hay DB para ellos) → requiere catálogo por filesystem.
