# Plan de desarrollo - Chatbot para estudios de cocinas y muebles a medida

## 1) Objetivo y alcance
- Producto B2B2C: los clientes directos son estudios/tiendas; los usuarios finales son sus leads de cocinas, armarios y muebles a medida.
- Meta: asistente 24/7 que califica, agenda y genera propuestas preliminares con IA, integrado en web/WhatsApp y operable desde un panel profesional.
- Alcance del plan: definición técnica y fases para llevar a MVP y posterior escalado (sin código aún).

## 2) Principios de producto
- Multi-tenant desde el diseño (un repositorio, múltiples tiendas, aislar datos/herramientas por tenant).
- Conversación híbrida (flujo determinista + IA) con guardrails y fallback seguro.
- Time-to-value corto: onboarding rápido por tienda, presets por sector, plantillas de flujo y textos.
- Observabilidad y trazabilidad: cada paso de conversación y decisión de IA es auditable.
- Seguridad por defecto: manejo de PII/WhatsApp, cumplimiento básico GDPR (consentimiento y derecho al olvido).
- Idiomas soportados desde v1: castellano, catalán, portugués, inglés; auto-detección por primer mensaje con fallback a idioma configurado por tenant.

## 3) Arquitectura conceptual (4 capas)
```
Frontend usuario final (widget web + WhatsApp) 
        |
API FastAPI (Capa Conversacional + Motor Bot)
        |
Servicios internos (IA, agenda, scoring, flujos, integraciones)
        |
Persistencia (PostgreSQL + Redis) + Almacenamiento (S3)
        |
Panel profesional (Streamlit) consumiendo la API
```
- Capa conversacional: widget JS whitelabel, canal web y WhatsApp Business API; gestiona sesión y entrega UI (botones, quick replies, inputs libres).
- Motor Bot: FlowEngine (máquina de estados), IA (NLP + generación), disponibilidad/agenda, personalización por tienda, lead scoring.
- Datos: PostgreSQL como fuente de verdad; Redis para sesiones activas y throttling; S3 para medios/exports.
- Panel profesional: Streamlit contra API; roles y configuración por tenant.

## 4) Stack técnico sugerido
- Backend: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, Uvicorn/Gunicorn.
- Datos: PostgreSQL 15+, Redis 6+; boto3 para S3 (o MinIO local).
- IA: OpenAI Chat/Assistants; providers intercambiables vía interfaz; rate limiting adaptable.
- Front widget: JS ligero (vanilla/TS) con build simple (Vite) y estilos whitelabel; canal WhatsApp vía webhook + callbacks.
- Panel: Streamlit + auth por tenant/rol; reutiliza API.
- Infra dev: Docker Compose (api, db, redis, minio opcional); Makefile para comandos.
- PDFs: WeasyPrint para generar resumen comercial con branding por tenant.

## 5) Multitenancy y configuración
- Esquema simple por tenant_id en todas las tablas de negocio (FK obligatoria, índices compuestos).
- Configuración por tenant versionada (JSON) para: textos, tonos, colores widget, flags de IA, reglas de scoring, agenda.
- Flujos editables por staff y por tenant (panel simplificado) con versionado vX, publish/unpublish y rollback de un clic.
- Aislar secretos por tenant (tokens WhatsApp, API keys) en tabla segura y cifrada (KMS/FERNET).
- Límite de tasa por tenant y por usuario para evitar abuso de API/IA; tope de coste IA por plan (Base 10 €, Pro 25 €, Elite 100 €).
- Rate limits concretos: 120 req/min por tenant; web widget 60 req/min por IP; WhatsApp 30 mensajes/min por número.

## 6) Modelado de datos (borrador)
- tenants (id, nombre, contacto, plan, flags IA, color/branding, idioma_default, timezone).
- flows (id, tenant_id, version, schema_json, estado, published_at, rollback_to_version, created_at).
- sessions (id, tenant_id, user_id/hash, canal, idioma_detectado, state, variables_json, last_block_id, expires_at).
- leads (id, tenant_id, session_id, origen, status, score, score_breakdown_json, metadata, idioma, timezone).
- appointments (id, tenant_id, lead_id, slot_start, slot_end, estado, origen, notas, reminder_status).
- configs (id, tenant_id, tipo, payload_json, version).
- messages (id, session_id, role, content, block_id, ai_meta, attachments).
- users (id, tenant_id, email, rol, hash_pwd/OAuth, status, mfa_enabled).
- analytics (id, tenant_id, fecha, kpi, valor, tags_json).
- files (id, tenant_id, lead_id, s3_key, tipo, meta).
- audits (id, tenant_id, entity, entity_id, action, actor).

## 7) Motores clave
- FlowEngine: lee flow JSON, evalúa condiciones, avanza bloques; API pura, sin IA; soporta publish/unpublish y rollback de versiones.
- SessionManager: guarda estado/variables en Redis (rápido) y vuelca a PostgreSQL (persistencia).
- IntentClassifier (IA): GPT-4.1 / 4.1-mini para extraer estilo, metros, presupuesto, urgencia; detección de PII; normaliza a esquema interno; fallback determinista al superar límite de coste.
- LeadScoring: regla base configurable por tenant; ponderación inicial: presupuesto 40 %, urgencia 25 %, metros 20 %, estilo definido 10 %, origen 5 %; umbrales frío 0–39, templado 40–69, caliente 70–89, premium 90–100; guarda breakdown por lead.
- AgendaEngine: calcula disponibilidad por reglas (horarios, festivos, duración, solapes, límites de franja); slots 30 min por defecto, configurables a 15/30/60; timezone por tenant y offset por usuario.
- PersonalizationEngine: aplica tono/longitud/tipo de cierre y plantillas por tenant; soporta idiomas definidos.

## 8) Flujo conversacional base (sin IA)
- Estructura JSON: bloques con id, type (message/buttons/input/date/range/media), prompts, opciones, next.
- Idiomas: UI y mensajes adaptados a idioma detectado o configurado por tenant; auto-detección en primer mensaje.
- Imágenes: entrada de fotos en v1 (WhatsApp); asociar a sesión y almacenar en S3; adjuntos permitidos (jpg/png/pdf) hasta 5 MB (fase 1.2).
- Retención S3: 30 días para adjuntos temporales; 180 días si están vinculados a leads; lifecycle rule para expiración automática.
- Validaciones: tipos de input, mínimos/máximos, normalización (p.ej. m2, rango de presupuesto).
- Persistencia: cada transición se guarda; reanudación posible por session_id.

## 9) Uso de IA (fase posterior)
- Extracción: prompts especializados por campo (estilo, metros, urgencia, presupuesto); GPT-4.1 / 4.1-mini.
- Generación: textos de bienvenida, cierre, micro-propuesta, follow-ups; control de temperatura y longitud.
- Límites: coste mensual por plan (Base 10 €, Pro 25 €, Elite 100 €); al pasar límite → extracción/generación determinista y respuestas cortas.
- Control horario y diario: slice de consumo por hora con recalculo cada 60 min; si supera límite horario → cambio a modelo barato y textos cortos; rollup diario alerta si >40 % del límite mensual.
- Alertas: 80 % del límite mensual → email + panel; 100 % → email + panel + modo low-cost automático.
- Resúmenes: “Resumen Comercial Profesional” con campos estructurados y texto corto; PDF con WeasyPrint y branding por tenant.
- Moderación: filtro automático (Moderation API); si contenido ofensivo → aviso amable y redirección a flujo determinista; sin escalado a humano obligatorio en MVP.
- Safety: moderación previa, truncado de contexto, red team list por tenant; reintento/fallback a flujo determinista.

## 10) Seguridad y cumplimiento
- PII: consentimiento explícito en bienvenida y en reserva; endpoint de borrado por usuario o por tenant (GDPR); retención por defecto 90 días para conversaciones y 2 años para leads/citas (configurable).
- Borrado masivo por tenant: DELETE `/tenant/{id}/purge`.
- Cifrado en tránsito (HTTPS) y en reposo (secrets + PII sensibles); rotación de tokens de WhatsApp; cifrar teléfono, email, dirección y fotos con KMS/Fernet.
- RBAC: roles (admin global, admin tienda, diseñador, comercial); autorización basada en tenant_id; 2FA opcional en planes Pro/Enterprise.
- Rate limiting y antiflood por IP/tenant/canal; logs sin PII por defecto.
- CORS: allowlist por tenant; widget firmado con JWT de 1h para restringir tenant_id a dominios autorizados.
- Rate limit público: 60 req/min por IP en widget; 10 req/min en endpoints sensibles (citas); bloqueo 10 min si se supera; firewall lógico para IP >400 req en 10 min.

## 11) Observabilidad y calidad
- Logs estructurados (JSON) con request_id/session_id/tenant_id; envío a CloudWatch (Loki opcional en 1.2); logs app 30 días, auditoría 90 días, métricas 15 días.
- Mascarado PII en logs: hash de phone/email; sin contenido crudo de usuario.
- Métricas: KPI de conversión, pasos del flujo, caídas, latencia IA, ratio de cita, no-shows.
- Trazas: OpenTelemetry opcional.
- Testing: unit (flows, scoring, agenda), contract tests de API, e2e de flujo base; fixtures de flows y seeds de tenants; cobertura mínima 70 % (FlowEngine 90 %+, agenda 85 %, IA extractor 70 %, API 60 %).
- Alertas tiempo real: Slack #alerts-prod (formato JSON compacto + link a trace/log) para 5xx repetidos, fallos de citas, timeouts IA >3s, webhooks WhatsApp tras 3 reintentos, healthcheck fail; umbral de repetición en 5 min. Email como fallback (equipo y tenants). Teams opcional para Enterprise (webhook por tenant).

## 12) Fases y entregables
- Fase 1 Fundamentos
  - Estructura repo: backend (FastAPI), frontend-widget, panel (Streamlit), infra (compose, scripts).
  - Docker Compose con api+db+redis (+minio opcional). .env.example, Makefile (run, test, format, lint, migrate).
  - CI básico (lint+tests).
  - Entrega: entorno local levanta, healthcheck `/health`.
- Fase 2 Modelado de datos
  - Tablas base alembic: tenants, users, flows, sessions, leads, appointments, configs, messages, files, audits.
  - Seeds: tenant demo, flow base v1, usuario admin demo.
  - Entrega: migraciones reproducibles; script `make seed`.
- Fase 3 Motor del chat (core)
  - FlowEngine y SessionManager funcionales; API `/chat/send` que recibe message y devuelve siguiente bloque.
  - LeadScoring stub (regla fija), IntentClassifier stub (sin IA, regex/reglas).
  - Idempotency-Key obligatorio en `/chat/send` para evitar duplicados.
  - Formato sugerido de Idempotency-Key: `{session_id}-{timestamp_ms}`.
  - Entrega: flujo determinista funciona sin IA; sesiones persistentes; versionado publish/unpublish.
- Fase 4 Flujo conversacional base
  - JSON del flujo completo (bienvenida → cierre) en 4 idiomas; validaciones; guardado de variables; soporte de imágenes.
  - Endpoints para obtener flujo y estado; reanudación de conversación.
  - Entrega: demo con flujo completo en web widget simple.
- Fase 5 IA integrada
  - Plugs IA para extracción y redacción con GPT-4.1/4.1-mini; prompts versionados; feature flags por tenant.
  - Resumen comercial estructurado y texto + PDF WeasyPrint con branding.
  - Límites de coste por plan; fallback determinista al superar tope; moderación activa.
  - Entrega: toggle IA on/off por tenant; fallback seguro.
- Fase 6 Agenda inteligente
  - Motor de disponibilidad con reglas; slots generados 15/30/60; reservas con bloqueo de solapes.
  - Recordatorios reales por WhatsApp y email; timezone por tenant y offset cliente.
  - Idempotency-Key obligatorio en `/appointments/book`; previene doble reserva.
  - Reintentos de webhooks de agenda/WhatsApp con backoff 5s/20s/60s (3 intentos) y log para reingesta manual.
  - Entrega: endpoint `/appointments/slots` y `/appointments/book`.
- Fase 7 Widget del chat
  - Burbuja JS embebible; states básicos; soporta botones/inputs; persistencia session_id en localStorage.
  - Personalización por tenant (colores, logo, textos básicos); auto-detección de idioma.
  - Entrega: script instalable con config mínima (tenant_id, endpoint).
- Fase 8 Panel Streamlit
  - Auth email+password; vistas de dashboard KPIs, leads, citas, configuración textual.
  - Ver resumen IA por lead; editar/publish flows desde panel simplificado; rollback.
  - Entrega: panel demo conectado a API demo.
- Fase 9 CRM básico (opc)
  - Kanban de leads, tareas, recordatorios; estados personalizables por tenant.
- Fase 10 Integraciones externas
  - WhatsApp Business API con Meta Cloud oficial; plantillas.
  - Google Calendar y OAuth Google/Microsoft en versión 1.2 (no MVP).
  - Facebook Leads, Zapier/Make, SES/Twilio.
- Fase 11 Modelo de suscripción
  - Planes y límites (Base/Pro/Elite); webhooks de Stripe; asignación de plan a tenant.
- Fase 12 Despliegue y escalabilidad
  - Infra AWS (ECS/EC2, RDS, Elasticache, S3, ALB, CloudFront); CI/CD GitHub Actions; backups y rotación de claves; VPC dedicada para Enterprise.

## 13) Hitos y timeline (sugerido)
- Semana 1-2: Fases 1-2 (infra, DB, seeds).
- Semana 3-4: Fases 3-4 (motor chat + flujo base).
- Semana 5: Fase 5 (IA inicial) detrás de feature flag y límites de coste.
- Semana 6: Fase 6 (agenda) + recordatorios.
- Semana 7: Fase 7 (widget) + integración.
- Semana 8: Fase 8 (panel mínimo) + cierre de MVP.
- Semana 9-10: Fase 1.2 (OAuth Google/Microsoft, Google Calendar, Loki opcional).
- Posterior: Fases 9-12 según tracción e integraciones vendidas.

## 14) Riesgos y mitigaciones
- Dependencia de IA externa: cacheo de prompts y fallback determinista; límites de costo por tenant.
- Calidad de extracción de datos: prompts específicos y tests de regresión con dataset sintético.
- Multi-tenant seguro: scoping por tenant en todas las queries; middleware de autorización.
- Latencia en WhatsApp/API: colas ligeras o reintentos idempotentes.
- GDPR/PII: consentimiento y endpoint de borrado; retención configurable.

## 15) Notas operativas
- Versionado: main + feature branches; PR obligatoria con tests.
- Configuración: `.env.example` documentado; secrets fuera del repo.
- Datos de demo: flujo base y tenant demo se publican para ventas.
- Documentación: README para levantar entorno; OpenAPI auto con FastAPI; playbook de soporte (reset sesión, borrar lead).
- API versionada desde MVP en `/v1/...`; mantener compatibilidad en releases mayores.
- Webhooks (WhatsApp) con reintentos automáticos 3x (5s/20s/60s) y log de fallos; reingesta manual desde panel interno.
- Staging separado con datos sintéticos (tenants/leads dummy, sin PII ni números reales); ventas usan tenant demo aislado en prod.
- Equipo: 2 devs (tú + Codex); priorizar alcance MVP y automatizar QA para sostener velocidad.

## 16) SLOs (MVP, promesa interna)
- API FastAPI: uptime 99.5 %; latencia p95 <1.0s y p99 <1.8s; tasa 5xx <0.5 %/día; timeouts IA <1 %.
- Widget web: uptime CDN 99.9 %; carga widget <200ms desde CloudFront; payload <60 KB; roundtrip usuario→API→respuesta p95 <1.2s.
- WhatsApp (lado interno): procesamiento webhook p95 <400ms; recepción→respuesta p95 <900ms.

## 17) Backups y recuperación ante desastres
- RDS PostgreSQL: snapshots automáticos cada 24h, retención 7 días; PITR habilitado.
- Redis: AOF cada 60s; backup diario a S3 en entornos staging/prod.
- SLO de recuperación: RPO <10 min para Redis, <24h para RDS; RTO <15 min para API+DB+Redis.
