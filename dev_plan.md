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

## 12) Fases y entregables (estado)
- Fase 1 Fundamentos (COMPLETADA)
  - Repo backend (FastAPI), frontend-widget, panel (Streamlit), compose, scripts; health `/v1/health` OK.
  - Entorno local levanta; .venv y deps dev instaladas.
- Fase 2 Modelado de datos (COMPLETADA)
  - Alembic tables: tenants, users, flows, sessions, leads, appointments, configs, messages, files, audits; seeds demo.
- Fase 3 Motor del chat (core) (COMPLETADA)
  - FlowEngine + SessionManager; `/v1/chat/send` con Idempotency-Key; versionado publish/unpublish de flujos.
- Fase 4 Flujo conversacional base (COMPLETADA)
  - Flujo base multi-idioma disponible; endpoints de estado y reanudación.
- Fase 5 IA integrada (PARCIAL)
  - Interfaces/flags IA listos; falta wiring de prompts/uso IA y control de costes.
- Fase 6 Agenda inteligente (PARCIAL)
  - Slots y reservas con idempotencia; pendiente recordatorios/webhooks de reintento y rate limits específicos.
- Fase 7 Widget del chat (COMPLETADA)
  - Burbuja JS, session_id en localStorage, personalización (colores/logo/textos), carga inicial `/v1/tenant/config` con auth y whitelisting de origen.
- Fase 8 Panel Streamlit (COMPLETADA mínimamente)
  - Login por tenant, vistas de leads/citas/historial/scoring/flujo, spinners y errores estandarizados; falta KPIs y rollback de flows desde UI.
- Fase 9 CRM básico (opc) (PENDIENTE)
- Fase 10 Integraciones externas (PENDIENTE)
- Fase 11 Modelo de suscripción (PENDIENTE)
- Fase 12 Despliegue y escalabilidad (PENDIENTE)

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

## 18) Relatorio situacional (estado real)
### 18.1 Lo que ya tienes funcionando
- Infra base: API FastAPI en contenedores estables; NGINX + SSL operativo.
- Panel Streamlit de tenant funcionando (login, leads/citas básicas).
- Widget listo a nivel de código (JWT corto renovable, allowed origins, session manager).
- Multitenant implementado: tablas, auth, middleware, límites IA; seeds de flows/leads/ia_usage listos.
- Traducción: motor y carrocería listos; falta el salpicadero profesional.

### 18.2 Gaps obligatorios (no opcionales)
- SuperAdmin Dashboard (separado de los tenants): crear/pausar/activar tenants, ver consumo IA global, errores, rotar tokens de widget, dominios autorizados, planes Base/Pro/Elite, mantenimiento por tenant, health global, impersonar tenant, gestionar usuarios internos. No visible para tenants.
- Panel de tenants real (no demo): leads con filtros, agenda/calendario, uso IA y límites, editor de textos/branding/widget, transcripts, logs de widget, versionado de flujo (publicar/rollback), snippet copy-paste del widget.
- Widget en producción: pruebas en dominio real para validar carga, CORS, validación de tenant_id/token, sesión persistente, latencia y flujo end-to-end.

### 18.3 Respuesta a “¿1 dashboard o 2?”
- Recomendado: dos paneles.
  - Dashboard 1 (SuperAdmin, solo tú): control total de plataforma, KPIs globales, límites IA, gestión de planes, rotación de tokens, dominios, impersonar, auditoría.
  - Dashboard 2 (Panel de tenant): solo sus datos (leads, citas, widget/branding, flujo, métricas, tokens y dominios autorizados, consumo IA).
- Unificar roles en un único panel es posible, pero no recomendable por riesgo de filtrado y UI/propósito distintos.

### 18.4 Plan ejecutivo (3 semanas de sprint)
- Semana 1: Construir SuperAdmin Dashboard (Streamlit separado o vista protegida). Endpoints GET/POST/PATCH /v1/tenants, PUT /v1/tenant/{id}/maintenance. UI: listado y creación de tenants (branding/plan/límites IA), estado, snippet autogenerado, métricas globales (leads totales, IA usage, error rate, últimos 50 errores).
- Semana 2: Mejorar Panel de tenants: navegación clara; leads con filtros; agenda visual; editor/publicación/rollback de flujo; consumo IA y límites; configuración del widget (colores/textos/allowed origins/token); transcripts/logs.
- Semana 3: Pruebas del widget en web real (opunnence.com/demo y dominio externo): CORS, expiración de token, recuperación de estado, callbacks al API, embudo widget→API→lead→panel; ajustes finales.

### 18.5 Indicadores de éxito
- Para ops: crear tenant en <20s; health global p95 <1s; IA cost por tenant preciso; cero cross-tenant; logs por tenant + global.
- Para tenants: instalar widget en <1 min; leads en tiempo real; branding editable sin soporte; métricas comprensibles.

### 18.6 Supuestos y confianza
- Confiabilidad del plan: 95 %.
- Supuestos: API estable (sí), widget funciona local (sí), Streamlit con roles (sí, con JWT/scopes), disponibilidad de tiempo para UI/UX paneles.

## 19) Decisión de arquitectura de paneles (ejecutada)
- Modelo elegido: **dos paneles separados**.
  - **SuperAdmin Dashboard** (dominio dedicado, p.ej. `admin.opunnence.com`): rol SUPER_ADMIN, controla tenants, planes, dominios, tokens de widget, mantenimiento, impersonación, métricas globales, alertas y auditoría. No accesible a tenants.
  - **Panel de Tenant** (actual Streamlit, dominio `panel.opunnence.com`): roles tenant (OWNER/ADMIN/AGENT), solo sus datos: leads, citas, flujo, branding/widget, métricas propias, tokens y allowed origins, consumo IA y límites.
- Justificación: menor riesgo de fuga cross-tenant, UI y propósito distintos, seguridad reforzada (2FA/allowlist opcional en SuperAdmin), mantenimiento independiente.

## 20) Autonomía técnica y pasos ejecutables inmediatos
1) **RBAC sólido y dominios**  
   - Migrar `users.role` a enum con SUPER_ADMIN/OWNER/ADMIN/AGENT/INTERNAL.  
   - Middleware de scopes: `/v1/admin/*` solo SUPER_ADMIN; impersonación emite JWT corto con claim `impersonate_tenant_id`.  
   - CORS/Origin estrictos por panel (admin y tenant), con allowlist separada.

2) **Endpoints SuperAdmin**  
   - CRUD tenants (plan, límites IA, allowed origins, maintenance flag).  
   - Rotar/regenerar tokens de widget + allowed_origins.  
   - Overview global: leads totales, IA usage global, error rate, health por servicio.  
   - Listado de errores/logs recientes con filtro por tenant.  
   - Impersonar tenant: POST `/v1/admin/impersonate/{tenant_id}` → JWT corto firmado.  
   - Auditoría: registrar acciones admin (create/update tenant, token, plan, maintenance, impersonar).

3) **UI SuperAdmin (Streamlit separada)**  
   - Secciones: Tenants (listado, crear/editar, maintenance), Tokens/Allowed Origins, Métricas globales, Errores, Impersonar.  
   - Requiere 2FA opcional y IP allowlist (NGINX) para SUPER_ADMIN.

4) **Refuerzo Panel de Tenant**  
   - Leads/citas con filtros avanzados; agenda visual.  
   - Consumo IA + límites y alertas; versionado flujo (publish/rollback) desde UI.  
   - Configurador de widget (branding, textos, allowed origins, token regen) y snippet copy-paste.  
   - Transcripts y logs de widget por tenant; exportación.  
   - Hardening CORS/Origin alineado con allowed origins por tenant.

5) **Pruebas del widget en dominio real**  
   - Checklist: CORS OK, token expira/renueva, estado persiste, latencia p95 <1.2s, embudo widget→API→lead→panel.  
   - Smoke E2E automatizados (Playwright/Vitest) apuntando a `opunnence.com/demo` y dominio externo de prueba.

## 21) Checklist de ejecución (runbook resumido)
- **Infra/seguridad**: SG 22/80/443, NGINX con HTTPS, CORS per-tenant, headers seguros, rate limit `/v1/chat`, systemd para compose.  
- **RBAC y datos**: migración enum roles, seeds usuario SUPER_ADMIN, scopes en middleware, auditoría de acciones admin.  
- **Endpoints admin**: CRUD tenants, toggle maintenance, rotar tokens widget, allowed origins, overview global, impersonate, errores recientes.  
- **Panel SuperAdmin (Streamlit separado)**: login con SUPER_ADMIN, listado/edición de tenants, mantenimiento, snippet widget, métricas globales, visor de errores, botón de impersonación.  
- **Panel tenant (refuerzo)**: filtros leads/citas, agenda, IA usage + límites, versionado flujo, configurador widget + snippet, transcripts/logs, export.  
- **Widget prod**: probar en dominio real (CORS, token renew, estado, latencia); smoke E2E automatizado; fallback offline verificado.  
- **Observabilidad**: health global p95<1s, dashboards IA/errores por tenant, alertas 5xx/latencia/IA>80%, CloudWatch/Loki (si aplica).  
- **Billing/planes**: UI admin para cambiar plan/IA limits, Stripe webhooks verificados, estados billing en tenants.  
- **Go-live**: checklist DNS + SSL + health `/v1/health` + widget en landing; acceso SuperAdmin separado; backups y rollback definidos.
