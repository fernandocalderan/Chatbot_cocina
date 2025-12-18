# Vertical registry

This registry defines the admin-controlled verticals and their default flow mapping.

Notes:
- Runtime flow source-of-truth is `backend/app/verticals/<vertical_key>/flow_base.json` (the old `backend/app/flows/*.json` is legacy and should not be used in runtime).
- New tenants must be created with a `vertical_key` from this registry (Admin panel enforces it).
- Tenants customize copy/UX via `tenant_flow_materials` (configs) which is merged onto the base flow at runtime (`apply_materials`) without changing the structure.

## Scopes (sub-verticals)

Some verticals define a `"scope"` and `"scope_definitions"` in `metadata.json` (e.g. `clinics_private`, `home_services`).

- When creating a tenant, the admin must select **1+ scopes** for those verticals.
- The selection is stored in `tenants.branding.vertical_scopes` (no schema migration required).
- Runtime flow is resolved as:
  - If exactly 1 scope is selected: apply `scope_definitions[scope].flow_overrides` to the base flow (or load `flow_scope_<scope>.json` if present).
  - Otherwise: use the base `flow_base.json`.
