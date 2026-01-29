# Release Checklist

Fecha: 2026-01-29

## Backend
- [ ] Migraciones aplicadas (alembic upgrade heads)
- [ ] Catalog OK (GLOBAL template publicado para el scope objetivo)
- [ ] Wizard OK (import + publish base)
- [ ] Tenant sync/diff OK (diff/sync/publish override)
- [ ] Resolver logs OK (source=TENANT_OVERRIDE)
- [ ] MULTIPLE_PUBLISHED = 0 (solo 1 publicado por grupo)
- [ ] Tenant sin vertical_key bloqueado con 409 en diff/sync/publish

## Panel (Streamlit)
- [ ] Tenants: diff/sync/publish funcionan y reflejan estado
- [ ] Warning + botones deshabilitados si tenant.vertical_key es vacío

## Evidencias
- [ ] backend/docs/debug/*.json
- [ ] backend/docs/debug/*.txt
