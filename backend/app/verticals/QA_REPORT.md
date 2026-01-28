# QA report · Verticales (home_services, kitchens, clinics_private)

> Este reporte refleja el estado actual de los archivos en `backend/app/verticals/`.
> El QA semántico es una lectura “mínima viable” para detectar huecos evidentes.

---

## 1) home_services

**Resumen**
- Scopes detectados: `instaladores_clima`, `instaladores_solar`, `reformas_parciales`, `carpinteria_metalica`, `cerramientos`, `persianas_toldos`, `electricidad`, `fontaneria`, `cristaleria`, `climatizacion_solar`, `reformas_carpinteria`, `fontaneria_electricidad`
- Flows detectados:
  - `flow_base_scope_climatizacion_solar.json`
  - `flow_base_scope_reformas_carpinteria.json`
  - `flow_base_scope_fontaneria_electricidad.json`
- Subflows por scope/grupo:
  - `climatizacion_solar`: `problema` = 4
  - `reformas_carpinteria`: `problema` = 5
  - `fontaneria_electricidad`: `problema` = 12

**Semántica mínima (checklist)**
- Identidad del experto: **parcial** (faltan prompts para 8 scopes).
- Goals/objetivo: **parcial** (solo cubierto en scopes con prompt/flow propio).
- Steps: **parcial** (solo 3 scopes tienen flow propio).
- CTA/agenda: **presente** en flows del vertical base; no verificado en scopes sin flow propio.
- Subflows: **cobertura parcial** (solo 3 scopes con problemas frecuentes).

**Hallazgos**
- Faltan `prompt_scope_*.txt` en scopes: `instaladores_clima`, `instaladores_solar`, `reformas_parciales`, `carpinteria_metalica`, `cerramientos`, `persianas_toldos`, `electricidad`, `fontaneria`.
- Scopes sin flow propio: se apoyan en `flow_base.json` (ok como fallback, pero incompleto para especialidad).
- Layout legacy de subflows (`subflow_scope_*`), no está en `subflows/<scope>/<group>/`.

**Recomendaciones**
- Crear prompts para scopes legacy y añadir flow_base_scope mínimo por scope crítico.
- Migrar subflows a carpeta `subflows/` o registrar explícitamente el layout legacy en la validación.
- Priorizar subflows para `electricidad` y `fontaneria` (alta frecuencia).

---

## 2) kitchens

**Resumen**
- Scopes detectados: `cocinas_completas`, `banos_lavaderos`, `muebles_medida`
- Flows detectados:
  - `flow_base_scope_cocinas_completas.json`
  - `flow_base_scope_banos_lavaderos.json`
  - `flow_base_scope_muebles_medida.json`
- Subflows por scope/grupo:
  - `cocinas_completas`: `problema` = 3
  - `banos_lavaderos`: `problema` = 4
  - `muebles_medida`: `problema` = 3
  - `default`: `intent` = 10 (pack de intención transversal)

**Semántica mínima (checklist)**
- Identidad del experto: **OK** (prompts por scope presentes).
- Goals/objetivo: **OK** (flujo cubre diagnóstico → propuesta → captura → CTA).
- Steps: **OK** (tipo proyecto, ubicación, estado, superficie, inversión, urgencia, contacto).
- CTA/agenda: **OK**.
- Subflows: **OK** en scopes principales.

**Hallazgos**
- Subflows `default/intent` no están referenciados por metadata (se reportan como orphans en QA).
- Layout legacy de subflows (`subflow_scope_*`).

**Recomendaciones**
- Registrar `default` como scope técnico en metadata o mover `intent` a grupos de scope.
- Mantener pack `intent` como biblioteca reutilizable (pero documentar su uso).

---

## 3) clinics_private

**Resumen**
- Scopes detectados: `dental`, `fisioterapia`, `osteopatia`, `psicologia_privada`, `podologia`, `rehabilitacion`, `fisioterapia_osteopatia`
- Flows detectados:
  - `flow_base_scope_dental.json`
  - `flow_base_scope_fisioterapia_osteopatia.json`
  - `flow_base_scope_psicologia_privada.json`
  - `flow_base_scope_podologia.json`
  - `flow_base_scope_rehabilitacion.json`
- Subflows por scope/grupo:
  - `dental`: `motivo_consulta` = 9
  - `psicologia_privada`: `motivo_consulta` = 3
  - `fisioterapia_osteopatia`: `motivo_consulta` = 3
  - `rehabilitacion`: `motivo_consulta` = 3
  - `podologia`: `motivo_consulta` = 3

**Semántica mínima (checklist)**
- Identidad del experto: **parcial** (faltan prompts para `fisioterapia`, `osteopatia`).
- Goals/objetivo: **OK** en flows existentes.
- Steps: **OK** (saludo, motivo, urgencia, primera visita, horario, ubicación, agenda).
- CTA/agenda: **OK**.
- Subflows: **OK** en 5 scopes; faltan problemas en `fisioterapia` y `osteopatia` (si se mantienen como scopes activos).

**Hallazgos**
- Scopes `fisioterapia` y `osteopatia` no tienen `flow_base_scope` ni `prompt_scope`.
- Layout legacy de subflows (`subflow_scope_*`).

**Recomendaciones**
- Consolidar scopes en `fisioterapia_osteopatia` o completar los individuales con prompts/flows/subflows.
- Migrar subflows a carpeta `subflows/` cuando se cierre la migración.

---

## Observaciones generales
- Se detecta uso del layout legacy de subflows en los 3 verticales.
- Hay scopes con fallback a `flow_base.json` sin identidad/guion propio.
- Los orphans detectados deben resolverse antes de `--strict`.
