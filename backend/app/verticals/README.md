# Vertical registry

This registry defines the admin-controlled verticals and their default flow mapping.

Notes:
- Runtime flow source-of-truth is `backend/app/verticals/<vertical_key>/flow_base.json` (the old `backend/app/flows/*.json` is legacy and should not be used in runtime).
- New tenants must be created with a `vertical_key` from this registry (Admin panel enforces it).
- Tenants customize copy/UX via `tenant_flow_materials` (configs) which is merged onto the base flow at runtime (`apply_materials`) without changing the structure.
