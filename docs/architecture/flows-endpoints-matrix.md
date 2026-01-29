# Flows Endpoints Matrix

> Objetivo: listar endpoints y filtros reales que pueden ocultar scopes/flows.

| Endpoint | Params | Filtros aplicados | Orden | Default | Riesgo |
|---|---|---|---|---|---|
| `GET /v1/admin/verticals` | — | Registry + filesystem (`verticals.list_verticals`) | por key | incluye scopes definidos en metadata | Medio (depende del FS) |
| `GET /v1/admin/verticals/{vertical}` | — | filesystem bundle | — | solo assets del vertical | Bajo |
| `GET /v1/admin/tenants` | `search` | DB tenants | — | lista básica | Bajo |
| `GET /v1/admin/tenants/{id}/flow` | — | **solo published** (resolver estricto) | `published_at DESC` | 409 si no hay publicado | Alto (oculta drafts/empty) |
| `GET /v1/admin/tenants/{id}/flow/versions` | `limit`, `include_schema` | DB flows por tenant | `version DESC` | no filtra published | Medio |
| `POST /v1/admin/tenants/{id}/flow` | body schema_json | crea published y despublica anteriores | — | fuerza published | Medio |
| `POST /v1/admin/tenants/{id}/flow/reset` | — | base flow desde vertical | — | published | Medio |
| `GET /v1/flows/current` | token tenant | **solo published** por tenant | `published_at DESC` | 409 si no hay publicado | Alto |
| `POST /v1/flows/update` | schema_json | crea nuevo published y despublica anteriores | — | published | Medio |
| `GET /v1/tenant/flows/subflows` | tenant auth | vertical + scope actual | — | filtra por scope | Medio |
| `GET /v1/tenant/flows/subflows/preview` | tenant auth | compone subflows + overrides | — | usa router/scope | Medio |
| `GET /v1/admin/subflows` | `vertical_key`, `scope`, `save_to` | filesystem subflows | — | lista catálogo | Bajo |

## Endpoints con riesgo de “ocultar scopes”
1) `GET /v1/admin/tenants/{id}/flow` y `GET /v1/flows/current`  
   - Filtran **solo published** → no muestran draft ni scopes vacíos.
2) Catálogo de verticals depende de filesystem/metadata, no DB.
3) Subflows por tenant usan scope actual → si scope no está en branding, no aparece.

## Notas de filtros implícitos
- **Resolver**: solo published, orden por `published_at DESC` y `version DESC`.
- **Scope**: derivado de `tenants.branding.vertical_scopes` (no hay tabla scopes).
- **Templates globales**: están en FS, no DB.
