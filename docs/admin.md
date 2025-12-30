# Panel y APIs de SuperAdmin

## Reconstrucción de flujos personalizados
- Documento de planificación: `docs/flow_rebuild_plan.md`.

## Localhost (quickstart)
- Levantar DB+Redis+API: `docker compose up -d --build`
  - API: `http://localhost:8100`
  - Postgres (host): `localhost:5433` (imagen `pgvector/pgvector`)
  - Redis (host): `localhost:6382`
- SuperAdmin panel (Streamlit): `scripts/run_admin_panel_local.sh` (por defecto `http://localhost:8502`)
- Tenant panel (Streamlit): `scripts/run_tenant_panel_local.sh` (por defecto `http://localhost:8501`)
- Si `8100` está ocupado, usa `API_PORT=8101 scripts/run_backend_local.sh` (backend fuera de docker) o cambia el mapping en `docker-compose.yml`.

## Acceso seguro
- Usa `ADMIN_API_TOKEN` como API key dedicada al panel de superadmin (no se acepta en chat/widget). Configúralo en `.env` y cambia el valor por un secreto fuerte por entorno (dev/stage/prod).  
- El panel `admin_panel` permite bypass OIDC si `ADMIN_API_KEY`/`ADMIN_API_TOKEN` está presente en el entorno.  
- Tokens `SUPER_ADMIN/ADMIN` están bloqueados en `/v1/chat`, `/v1/widget` y `/v1/flows`. Tokens `WIDGET` están bloqueados en `/v1/admin/*`.
- Rate limit defensivo para `/v1/admin/*`: 30 req/min por IP.

## Impersonación
- Al generar un token de impersonación en el panel, aparece un banner rojo con “Salir de impersonación” para limpiar el token local.  
- El token de impersonación es de tipo `TENANT` con rol `IMPERSONATED`; no puede acceder a `/v1/admin/*`.

## Auditoría
- Toda acción de superadmin (crear/editar tenant, mantenimiento, emisión de widget token, impersonate) se registra en `audits` con `actor`, `tenant_id` y `action`.

## Recordatorio de rotación
- Cambia `ADMIN_API_TOKEN` periódicamente y por entorno.  
- No reutilices tokens de superadmin en el widget ni en el panel de tenants.
