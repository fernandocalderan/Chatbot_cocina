# Panel y APIs de SuperAdmin

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
