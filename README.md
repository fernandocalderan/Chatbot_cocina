# Observabilidad y Logging

- Logs estructurados (JSON) con contexto `request_id`, `tenant_id`, `session_id` se generan por defecto con Loguru.
- PII y contenidos sensibles se enmascaran; no se loguean emails/teléfonos en texto plano.
- Exporters opcionales:
  - **Loki**: establecer `LOG_EXPORTER=loki`, `LOKI_ENDPOINT=https://<url>/loki/api/v1/push`, y `LOKI_BASIC_AUTH=user:pass` (si aplica).
  - **CloudWatch**: `LOG_EXPORTER=cloudwatch`, `CLOUDWATCH_LOG_GROUP=<grupo>`, `CLOUDWATCH_LOG_STREAM=<stream>`.
  - Por defecto solo se escribe en archivo `backend/app/logs/app.log` y stdout.
- Activar/desactivar en cada entorno vía variables de entorno; no se guardan secretos en el repositorio.
