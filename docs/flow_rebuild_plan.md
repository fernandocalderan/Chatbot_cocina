# Plan de reconstrucción del sistema de flujos personalizados (multi‑tenant)

## 0) Objetivo
Reconstruir el sistema de flujos para que **cada tenant** tenga un flujo **generado por IA y editable** en su propio panel, usando como base:
- `vertical` + `scopes` (definidos al crear el tenant desde SuperAdmin).
- el **plan de uso de IA** del tenant (base/pro/elite, límites y features).
- **documentos del negocio** cargados por el tenant (precios, horarios, servicios, materiales, políticas, etc.), con **búsqueda semántica**.

## 0.1) Modelo TO‑BE (v1) — Router + Sub‑flows (sin conditions)
Para que el flujo se perciba “inteligente” **sin usar `condition`** (prohibido en v1 por seguridad), el recorrido se diseña con un patrón:

- **Router flow** (por scope): solo clasifica intención inicial y termina en `end`.
- **Motor (backend)**: al terminar el router, decide qué sub‑flow ejecutar según el valor guardado (`save_to`) y una tabla de mapeo (`routes_file`).
- **Sub‑flows**: conversaciones completas, humanas y contextuales, editables por humanos. No contienen decisiones ni efectos secundarios.

Principios:
- Los flows JSON describen conversación, nunca decisiones.
- IA solo puede generar bloques seguros (whitelist) y no puede generar `condition` ni `internal`.
- Los **sub‑flows son entidades de primer nivel** (flow completo con `version`, `start_block`, `blocks{}`), visibles y editables.

Estructura de assets por vertical:
- `flow_base_scope_<scope>.json` → router del scope (flow completo).
- `router_routes_scope_<scope>__<save_to>.json` → mapeo `intent_key → subflow_file` (fuera del flow JSON).
- `subflow_scope_<scope>__<save_to>__<intent>.json` → sub‑flow (flow completo).

Personalización por tenant:
- El tenant edita **textos y opciones** del router (draft/publish en DB).
- El tenant puede editar **textos y opciones** de sub‑flows mediante overrides persistidos en DB (sin tocar estructura).

El objetivo es cambiar la estructura actual hacia un modelo donde:
1) el tenant carga documentos,
2) ejecuta el comando **“Crear flujo”**,
3) la IA genera un flow JSON válido,
4) el tenant puede **editar bloque por bloque** (pregunta por pregunta),
5) publica y el **widget usa el flujo publicado**.

---

## 1) Estado actual (AS‑IS) — análisis profundo

### 1.1 Runtime del flujo (backend)
- Motor determinista: `backend/app/core/flow_engine.py` (state machine por `blocks` + `start_block`).
- Orquestación de conversación: `backend/app/api/chat.py` interpreta tipos de bloque y guarda variables (`save_as/save_to`), genera opciones, valida inputs y dispara IA/acciones.
- Router + Sub‑flows (v1-safe):
  - El router termina en `end`.
  - El motor lee `config.router.routes_file` y carga el sub‑flow correspondiente.
  - El motor persiste el sub‑flow activo en sesión (`_active_flow`) para continuar el diálogo en llamadas siguientes.
- Widget runtime:
  - Resuelve flow + materiales y devuelve `runtime/config`: `backend/app/api/widget.py`.
  - El widget se guía por `text` + `options` + `type` (no por el JSON completo).

Tipos de bloque observados en flows actuales (ej. kitchens):
- `message`, `input`, `buttons/options`, `calendar/appointment`, `internal`, `end`.

### 1.2 Fuentes del flujo (verticals/scopes/DB)
Hoy el flow efectivo puede venir de:
1) **Vertical base** en repo: `backend/app/verticals/<vertical_key>/flow_base.json`.
2) **Scope overrides** (si hay exactamente 1 scope): merge de `metadata.json:scope_definitions[scope].flow_overrides` o archivo `flow_scope_<scope>.json`.
   - Resolver: `backend/app/services/flow_templates.py` + docs: `backend/app/verticals/README.md`.
3) **Custom flow publicado** por tenant en DB (tabla `flows`):
   - Modelo: `backend/app/models/flows.py`.
   - Resolver: `backend/app/services/flow_resolver.py` (usa `active_flow_id` o último `published`).
   - Control de “usar custom o no”: `tenants.branding.custom_flow_enabled` (helper `tenant_custom_flow_enabled` en `backend/app/services/verticals.py`).

Nota: hoy, si un tenant tiene múltiples scopes y `custom_flow_enabled` está apagado, el runtime usa el `flow_base.json` (no aplica overrides múltiples). En el TO‑BE esto es aceptable como fallback; el comportamiento “multi‑scope real” vive en el **custom flow generado**.

### 1.3 Personalización “sin tocar estructura”: Materials
Existe un overlay de copy/UX por tenant:
- Config tipo `tenant_flow_materials` (`backend/app/models/configs.py`), aplicado en runtime con `backend/app/services/flow_templates.py:apply_materials`.
- Editado desde panel tenant por `backend/app/api/tenant_automation.py` (draft/publish/rollback de materials).
- También contiene:
  - `automation` (ai_level, ai_steps, saving_mode… capado por plan).
  - `knowledge_files` (lista de `file_id`).

### 1.4 Documentos / KB (ya existe base)
- Uploads por tenant: `backend/app/api/files.py` → tabla `files` (`backend/app/models/files.py`).
- Extracción:
  - PDF: `pypdf` al subir (y endpoint manual `/files/{id}/extract`).
  - Imágenes: opcional con IA (`use_ai=true`) vía `file_text_extractor`.
- Inyección de “KB prompt” (texto recortado) para IA: `backend/app/services/knowledge_base.py`.

### 1.5 Frontends (paneles) relacionados con flujos
SuperAdmin (`admin_panel`):
- Gestión de tenants + toggle `custom_flow_enabled` y editor JSON de flow publicado: `admin_panel/pages/02_🏢_Tenants.py` (usa endpoints `/v1/admin/tenants/{id}/flow`).
- Gestión de verticals y assets: `admin_panel/pages/03_🧩_Verticals.py` (edita `flow_base.json`, prompts, etc.).
  - Router + Sub‑flows:
    - botón de “Scaffold subflows desde opciones” crea `router_routes_scope_*` + `subflow_scope_*` (flow completo).
    - editor JSON por sub‑flow.
  - Nota v2: los `flow_*.json` del catálogo de verticales se tratan como **plantillas/fallback/seed**; el flow “real” del tenant vive en DB y la “base” de generación vive en **prompts**.

Tenant panel (`panel`):
- `Automatización`:
  - `panel/pages/04_Automatizacion.py`: edita textos por bloque **guardando flow completo** vía `/flows/update`.
  - `panel/pages/automatizacion.py`: edita/publishes `tenant_flow_materials` (copy, botones, nivel IA, knowledge_files, etc.).
- Bloqueo actual importante:
  - `backend/app/api/flows.py:/flows/update` **prohíbe** actualizar flows si el tenant tiene `vertical_key` (`vertical_flow_locked`).
  - Resultado: el tenant “vertical” no puede estructuralmente publicar su propio flow desde su panel; depende de base/overrides/materials o de SuperAdmin.
  - En v2 esto se reemplaza por `tenant/flows` (draft/publish) y overrides de sub‑flows (solo textos/opciones).

---

## 2) Gaps / riesgos (por qué hay que reconstruir)

### 2.1 Gaps funcionales vs objetivo
- No existe un **pipeline** “docs → comando → IA genera flow → editor por bloque → publish”.
- La personalización por tenant está dividida entre:
  - flow base (repo),
  - overrides por scope (repo),
  - materials (DB),
  - custom flows (DB, pero controlado hoy por SuperAdmin y/o bloqueado para tenants verticales).
- La UX actual del tenant se centra en copy, no en “crear flujo” con IA ni en edición estructural sencilla.

### 2.2 Riesgos técnicos actuales que impactan en IA‑generated flows
- Validación de flow muy básica (refs de bloques) en `backend/app/services/vertical_admin.py:validate_flow_schema`:
  - No valida coherencia de `type`, `save_as`, `options`, `action`, ni contratos de chat/widget.
- `FlowEngine` soporta `condition` con `eval(expr, {}, ctx)`:
  - IA no debería generar expresiones arbitrarias; riesgo de seguridad y de mantenimiento.
- Acciones internas:
  - existen bloques `internal` y acciones/steps en `backend/app/core/actions.py`.
  - IA no debe poder inventar acciones desconocidas.

---

## 3) Target (TO‑BE): nuevo flujo “personalizado por IA” por tenant

### 3.0 Decisiones confirmadas (inputs del producto)
- `scope` es **sub‑vertical** y un tenant puede tener **múltiples scopes** (la IA los lee todos para construir el flujo).
- “Crear flujo por IA” disponible en todos los planes, con cuota mensual incluida:
  - Base: 1 creación IA / mes
  - Pro: 3 creaciones IA / mes
  - Elite: 5 creaciones/regeneraciones IA / mes
  - Extra: permitir más creaciones con **cobro adicional**.
- Idiomas: el flow se genera **multi‑idioma**.
- Edición en panel tenant (v1): **manual ilimitada** pero solo de **textos y opciones** (incluye crear botones/opciones). Sin edición estructural (sin cambiar `next`, sin reordenar, sin agregar/quitar bloques).
- Conocimiento: se requiere **búsqueda semántica** sobre documentos. Tipos: **PDF, imágenes, XLSX**.
- Seguridad por diseño en flows IA (v1): la IA solo genera capa conversacional (whitelist). Prohibidos `condition` e `internal` en generación.

### 3.1 Principio base
Cada tenant se define por:
- `vertical_key`
- `scopes` (0..N, sub‑verticals)
- `plan` (y límites/features de IA)

Y tiene su propio:
- **Knowledge Base** (documentos del negocio, gestionados en su panel).
- **Flow** (JSON schema compatible con runtime actual).

### 3.2 Nuevo concepto: “Flow Blueprint Prompt”
En vez de que el flow base sea un JSON fijo, el “base” de construcción será un **prompt**:
1) Prompt vertical (ya existe): `backend/app/verticals/<vertical>/prompt_vertical.txt`
2) Prompts por scope (nuevo, 0..N): por ejemplo `prompt_scope_<scope>.txt` o `metadata.json:scope_definitions[scope].prompt_overrides` (se concatenan para todos los scopes del tenant)
3) Prompt de “generación de flow” (nuevo, global): instruye al LLM a devolver un JSON **estrictamente válido** (schema + allowed block types/actions + naming rules).
4) “Plan policy”: restricciones por plan (campos que se permiten, tipo de automations, bloque AI, etc.).
5) “Business context” desde documentos: resumen/snippets vía `knowledge_base.build_knowledge_prompt(...)` (y/o un resumen “curado” por el tenant).

Output: `flow.schema_json` listo para validar → guardar → editar → publicar.

### 3.3 Flujo operacional propuesto (tenant)
1) Tenant entra en “Documentos” → sube PDFs/imágenes → verifica texto extraído.
2) Tenant selecciona qué docs alimentan el flujo/IA (KB).
3) Tenant pulsa **“Crear flujo”** (comando).
4) Backend genera un **draft**:
   - `flow.estado = "draft"`
   - `flow.schema_json = <JSON generado>`
   - `flow.meta` (propuesto) con: `prompt_hash`, `file_ids`, `model`, `tokens`, `cost`, `errors`, etc.
5) Tenant ve el flujo en UI “pregunta por pregunta” (bloque por bloque):
   - edita textos (multi‑idioma si aplica),
   - edita opciones/labels,
   - (modo avanzado) ajusta `next`/ramas y variables.
6) Tenant publica → backend crea versión `published`, setea `active_flow_id` y habilita `custom_flow_enabled`.
7) Widget usa el flujo publicado automáticamente (sin cambios en contrato).

---

## 4) Estrategia de reestructuración con mínima ruptura (backend primero)

### 4.1 Mantener contratos existentes
No romper:
- `resolve_runtime_flow(...)` y tabla `flows` (ya soporta versiones y `active_flow_id`).
- Contratos del widget y de `chat.py` (tipos de bloque esperados).
- `tenant_flow_materials` como fuente de:
  - `automation` (capado por plan),
  - `knowledge_files` (selección KB),
  - copy overlay (si se decide mantenerlo en transición).

### 4.2 Cambios backend necesarios (propuestos)
1) **Nuevos endpoints tenant** para flows (paralelos a admin, pero scoping por tenant):
   - `POST /v1/tenant/flows/generate` (crea draft por IA)
   - `GET /v1/tenant/flows/draft`
   - `PUT /v1/tenant/flows/draft` (guardar edición)
   - `POST /v1/tenant/flows/publish`
   - `GET /v1/tenant/flows/versions`
   - `POST /v1/tenant/flows/rollback`
   - `POST /v1/tenant/flows/reset` (volver a base vertical+scopes)
2) Reusar `flows.estado` realmente (`draft/published/archived`) en vez de “solo published”.
3) Validación reforzada para flows generados/guardados:
   - Baseline: `validate_flow_schema` (refs).
   - Añadir: allowed `type`, required fields por type, allowed `internal.action`, saneamiento de `condition` (o prohibirla en generación).
4) Generación IA:
   - Implementar `FlowGeneratorService` (nuevo) que compone prompts, llama LLM, parsea JSON y valida.
   - Registrar coste/uso contra el tenant en `ia_usage.call_type="flow_generation"`.
   - Enforzar **cuota mensual de creaciones** por plan (Base/Pro/Elite) y permitir overage con cobro (billing).
5) Búsqueda semántica (KB):
   - Introducir indexado por tenant: extracción → chunking → embeddings → búsqueda top‑k en runtime.
   - Reemplazar/acompañar el “prompt largo” de `knowledge_base.build_knowledge_prompt(...)` con retrieval dinámico (RAG) para precios/horarios/políticas.
   - Recomendación (v1): `pgvector` + tabla `kb_chunks` (tenant_id, file_id, chunk_idx, text, embedding, meta).
   - Embeddings recomendados (OpenAI, multi‑idioma): `text-embedding-3-small` (coste) o `text-embedding-3-large` (calidad).
   - XLSX: extracción a texto por hoja/tabla (por filas) y chunking por rangos (p.ej. 20–50 filas por chunk), preservando cabeceras.

### 4.3 “Vertical locked” (decisión clave)
El bloqueo actual (`/flows/update` devuelve `vertical_flow_locked`) se debe reemplazar por:
- “No edites el base del vertical desde tenant” (ok),
- pero **sí** permitir que el tenant edite/publica **su custom flow** una vez generado.

Esto mantiene la idea de “vertical base protegida” sin impedir el objetivo de “flujo personalizado por tenant”.

---

## 5) Cambios frontend (panel tenant) para soportar el nuevo flujo

### 5.1 Páginas / secciones nuevas
1) **Documentos / Base de conocimiento**
   - listar archivos (`GET /v1/files`)
   - subir (`POST /v1/files/upload`)
   - extraer texto si falta (`POST /v1/files/{id}/extract`)
   - seleccionar cuáles alimentan el flujo (persistir en `tenant_flow_materials.knowledge_files`)
2) **Flujo**
   - botón “Crear flujo” (dispara generación)
   - vista de bloques ordenados + edición por bloque
   - publish/rollback
   - preview (mostrar “effective flow” + mensajes como los vería el widget)

### 5.2 UX del editor (simple, editable por usuario dashboard)
- Vista “lista de preguntas” (block list):
  - label: primera línea del texto + tipo
  - acciones por bloque: editar texto, editar opciones, editar variable destino (`save_as`) si aplica
- Modo avanzado:
  - (v1) NO disponible: no se edita `next`/ramas ni validaciones ni estructura. Solo textos y opciones.

Editor de sub‑flows (v1):
- Lista de sub‑flows disponibles (derivada de `routes_file` del router).
- Al elegir un sub‑flow:
  - lista de bloques con edición de `text` + `options[].label`.
  - cambios se aplican como override por tenant (persistente), sin modificar el asset del vertical.

---

## 6) Entregables / fases recomendadas
1) **Fase A (infra + backend)**: endpoints tenant flows + validación + draft/publish + auditoría.
2) **Fase B (panel)**: UI Documentos + UI Crear flujo + editor básico por bloque.
3) **Fase C (IA)**: FlowGeneratorService + prompts (vertical/scope/plan) + guardrails.
4) **Fase D (migración)**: feature flag por tenant + rollback seguro.

---

## 7) Preguntas abiertas (huecos) para cerrar antes de implementar
Pendientes de confirmar (para bloquear el diseño técnico):
1) **Bloques permitidos en flows generados por IA (v1)** (confirmado):
   - Whitelist: `message`, `input`, `buttons/options`, `calendar/appointment`, `attachment`, `end`.
   - Prohibido que la IA genere `condition` (por riesgo técnico y de seguridad del `eval` actual). Las condiciones se incorporan en una fase futura con DSL/UI segura definida por humanos y validada por el sistema.
   - Prohibido que la IA genere `internal`. Los bloques internos (scoring, persistencia, analytics, auditoría, etc.) se **inyectan solo por el sistema** bajo reglas predefinidas y listas blancas.
2) **Cuotas IA por plan** (confirmado):
   - Edición manual: ilimitada en todos los planes.
   - Generaciones/regeneraciones IA: limitadas por plan (Base 1/mes, Pro 3/mes, Elite 5/mes) + overage cobrado.
3) **Búsqueda semántica (RAG)**: ¿preferencia por `pgvector` en Postgres vs un servicio externo? (mi recomendación: `pgvector` para empezar, multi‑tenant por `tenant_id`).
4) **XLSX**: ¿qué estructura típica tienen? (precios/tabla por hoja). Define si se debe indexar por filas, por hoja completa o por rangos.

---

## 8) Próximo paso
Para no bloquear implementación, propongo asumir:
- RAG: `pgvector` en Postgres (multi‑tenant por `tenant_id`).
- XLSX: extracción a texto por hoja + chunking por rangos de filas preservando cabeceras.

Si estás de acuerdo, el siguiente paso es ejecutar el plan técnico de la sección 9.

---

## 9) Estado de implementación (local)
Implementado en el repo:
- Motor Router → Sub‑flow (handoff fuera del JSON): `backend/app/api/chat.py`.
- Assets por scope + sub‑flows: ver `backend/app/verticals/<vertical>/flow_base_scope_<scope>.json` y `subflow_scope_*`.
- Autoría en SuperAdmin:
  - router + scaffold subflows + editor JSON: `admin_panel/pages/03_🧩_Verticals.py`.
- Panel tenant (v2):
  - flow draft/publish y editor por bloque: `panel/pages/flujo_v2.py`.
  - editor de sub‑flows (textos/opciones) sobre overrides por tenant.

Notas:
- v1: la IA no genera `condition` ni `internal`; el motor mantiene el control de decisiones y efectos secundarios.
- v2: el router publicado del tenant vive en DB (`flows`); los sub‑flows por defecto viven en assets del vertical y se personalizan con overrides por tenant.

---

## 9) Plan técnico (senior) para reemplazo total del flujo antiguo por el nuevo

### 9.1 Principios de migración (seguridad + cero downtime)
- Migración por **feature flag por tenant**: `tenants.branding.flow_system = "v2"` (nuevo), con fallback inmediato a v1.
- La v2 no rompe el widget ni `/v1/widget/*`: el runtime sigue usando el mismo contrato de `chat.py`/FlowEngine.
- La IA no controla lógica ni side effects:
  - la IA genera solo bloques conversacionales whitelisted,
  - el sistema **sanitiza** (strip) campos no permitidos (incl. `actions`),
  - el sistema **inyecta** lógica interna (scoring, persistencia, auditoría) con reglas predefinidas.

### 9.2 Cambios de dominio y datos (DB)
**Nuevas tablas (propuestas)**
1) `flow_generations` (auditoría + cuota):
   - `id`, `tenant_id`, `created_at`, `status` (`queued|running|failed|succeeded`),
   - `requested_by_user_id` (opcional), `source` (`tenant_panel|migration|admin`),
   - `scopes`, `languages`, `model`,
   - `selected_file_ids` (o tabla relacional),
   - `result_flow_id` (FK a `flows.id`), `error`,
   - `tokens_in/out`, `cost_eur`, `call_type="flow_generation"`.
2) RAG:
   - `kb_chunks` con `pgvector`:
     - `id`, `tenant_id`, `file_id`, `chunk_idx`, `text`, `embedding vector`, `meta` (hoja/rango/offsets), `created_at`.

**Tablas existentes que se reutilizan**
- `flows` (versionado del flow por tenant) + `tenants.active_flow_id`.
- `configs`:
  - mantener `tenant_flow_materials` en transición, pero en v2 se usa principalmente para `automation` + `knowledge_files` (y no como overlay de copy si decidimos “single source of truth” en `flows.schema_json`).
- `files` (documentos) como fuente de extracción/indexado.

**Migrations**
- Alembic: crear `flow_generations`, habilitar `pgvector`, crear `kb_chunks`.

### 9.3 Contrato del Flow JSON (v2) y validación estricta
**Whitelist de tipos (v1 IA)**
- `message`, `input`, `buttons/options`, `calendar/appointment`, `attachment`, `end`.

**Validator v2 (nuevo servicio)**
- Validación estructural:
  - `start_block` existe y apunta a un bloque real.
  - todas las referencias `next`/`next_map`/`branches` apuntan a IDs válidos.
- Validación semántica por tipo:
  - `input`: requiere `save_as` (para no perder datos).
  - `buttons/options`: requiere `options[]` con `id/value` estable + `label` por idioma.
  - `calendar/appointment`: requiere `save_as` y contrato de slot.
  - `attachment`: requiere `save_as`.
- Sanitizer:
  - elimina `condition`, `internal`, `ai_generate`, `ai_extract` y cualquier tipo fuera de whitelist.
  - elimina `actions` si vienen del output IA (solo sistema puede inyectar acciones).
  - elimina campos desconocidos/no permitidos por tipo.

### 9.4 Backend: nuevos endpoints (tenant) y comportamiento runtime
**Tenant flows (v2)**
- `POST /v1/tenant/flows/generate`
  - Enforza cuota mensual (Base/Pro/Elite), registra `flow_generations`, llama IA, valida/sanitiza, guarda como `flows.estado="draft"`.
- `GET /v1/tenant/flows/draft` / `GET /v1/tenant/flows/published`
- `PATCH /v1/tenant/flows/draft/blocks/{block_id}`
  - Solo permite editar: `text` (multi‑idioma) y `options` (ver restricciones abajo).
- `POST /v1/tenant/flows/publish`
  - Crea nueva versión `published`, setea `active_flow_id`, activa `branding.custom_flow_enabled=true`.
- `GET /v1/tenant/flows/versions` + `POST /v1/tenant/flows/rollback`
- `POST /v1/tenant/flows/reset`
  - Resetea a snapshot del flujo base (vertical+scopes) o “flow inicial” migrado.

**Restricciones de edición de opciones (para no tocar estructura)**
- Permitir siempre editar labels de opciones existentes.
- Permitir “crear opción” solo si el bloque es **no‑branching**:
  - si el bloque usa `next` fijo (sin `next_map/branches`), se puede añadir opciones nuevas (todas avanzan al mismo `next`).
  - si el bloque usa `next_map/branches`, solo se permiten edits de label (no añadir/remover IDs) en v1.

**Runtime selector**
- Cuando `branding.flow_system == "v2"`:
  - usar siempre `active_flow_id` (o último `published`) desde DB,
  - ignorar overlays legacy de copy (`tenant_flow_materials.content.{welcome,closing,questions,buttons}`) para evitar doble fuente de verdad,
  - mantener `tenant_flow_materials.visual`, `tenant_flow_materials.automation`, `tenant_flow_materials.knowledge_files` (y `errors/tone/language` como UI defaults) porque no alteran estructura.
- Cuando no:
  - comportamiento actual (vertical+scopes + materials + toggle `custom_flow_enabled`).

### 9.5 Generación de flow por IA (pipeline)
1) Input:
   - `vertical_key`, `scopes[]`, `plan`, `languages[]`, `knowledge_files[]`.
2) Contexto:
   - prompts (archivos en `backend/app/verticals/<vertical_key>/`):
     - base: `prompt_vertical.txt` (+ opcional `prompt_vertical_extension.txt`),
     - por scope (0..N): `prompt_scope_<scope>.txt` (se concatenan para *todos* los scopes del tenant),
     - policy de plan + JSON schema/ejemplos (en system prompt del generador).
   - business knowledge:
     - v1: resumen corto + “facts” desde documentos seleccionados (sin inventar).
     - v2: RAG (top‑k chunks por queries tipo “servicios”, “precios”, “horarios”, “materiales”).
3) Output:
   - JSON parseable, validado, sanitizado.
4) Persistencia:
   - `flows.estado="draft"` (v+1), `flow_generations.result_flow_id=<draft_id>`.
5) Publicación:
   - solo por acción explícita del tenant.

### 9.6 RAG (búsqueda semántica) — implementación incremental
**Indexado**
- Trigger al subir/extraer archivo:
  - PDF: usar extracción existente.
  - Imagen: extracción con IA existente.
  - XLSX: nueva extracción (por hoja/tabla) → texto.
  - Chunking + embeddings → `kb_chunks`.

**Retrieval**
- Función: `search_kb(tenant_id, query, top_k)` → chunks.
- Uso:
  - en `ai_reply`: añadir “Contexto encontrado” con chunks + fuente/archivo.
  - en `flows/generate`: queries predefinidas para construir un “business context” estable.

### 9.7 Panel tenant (UX) — sustitución del flujo antiguo
**Nueva navegación**
- “Documentos” (KB): upload + extracción + selección para KB.
- “Flujo”:
  - botón “Crear flujo (IA)” (muestra cuota restante y overage),
  - editor por bloque:
    - texto multi‑idioma,
    - opciones (labels + crear opción en no‑branching),
  - publish/rollback,
  - preview (effective flow).

**Deprecación del flujo antiguo**
- Ocultar/retirar en UI:
  - `panel/pages/04_Automatizacion.py` (edición de flow completo vía `/flows/update`).
  - mantener temporalmente `panel/pages/automatizacion.py` solo para `visual` + `automation` + KB selection; deshabilitar en v2: selección de `flow_id` y overrides de preguntas/botones/welcome/closing.

### 9.8 Migración de datos (cutover por tenant)
**Objetivo**: pasar a “single source of truth” en `flows.schema_json` sin romper operación.

Fase 1 — Infra v2 (sin activar)
- Crear tablas + endpoints + validator/sanitizer/injector.
- Añadir `branding.flow_system` (sin UI).

Fase 2 — Migración inicial sin IA (recomendada)
- Para cada tenant existente:
  - resolver su flujo efectivo actual (vertical+scopes + materials aplicados),
  - guardar snapshot como `flows.estado="published"` (nueva versión “migration_v2_seed”, sin gastar cuota IA),
  - setear `active_flow_id` y `branding.flow_system="v2"`.
- Resultado: el tenant ya corre con flow en DB y el sistema antiguo deja de ser fuente de verdad.

Fase 3 — Activación UI v2
- Desplegar panel con “Documentos” + “Flujo”.
- Permitir regeneración IA dentro de cuota por plan.

Fase 4 — Limpieza/deprecación
- Marcar `/flows/update` como legacy y deshabilitarlo para tenants v2.
- (opcional) migrar/retirar el overlay de copy en `tenant_flow_materials` para evitar doble configuración.

### 9.9 Rollback (por tenant)
- Flip de flag: `branding.flow_system="v1"`:
  - runtime vuelve a vertical+scopes + materials.
- Mantener `flows` versionados para forward‑reapply cuando se re‑active v2.

### 9.10 Observabilidad y criterios de aceptación (DoD)
**Métricas**
- `flow_generation_requests_total`, `flow_generation_failures_total`, `flow_publish_total`.
- `kb_index_jobs_total`, `kb_search_latency_ms`, `kb_search_hits_total`.
- p95 de `/v1/widget/message` antes/después.

**DoD técnico**
- 0 cross‑tenant leakage (scoping por `tenant_id` en todo).
- Cuotas IA por plan funcionando + overage registrado.
- Widget no se rompe (smoke test e2e).
- Editor tenant limita cambios a textos/opciones (sin tocar estructura).
