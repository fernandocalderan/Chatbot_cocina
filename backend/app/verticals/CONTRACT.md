# Contrato oficial de verticales (Source of Truth)

## Definiciones
- **Vertical (dominio)** → **Scope (especialidad)** → **Flow (playbook conversacional)** → **Subflows (problemas frecuentes / intent packs)**.

## Regla mental
**“Flow NO es un grafo técnico; es un Playbook conversacional editable en bloques humanos (Identidad/Objetivo/Guion/Reglas).”**

## Layout de filesystem esperado (normativo)
```
backend/app/verticals/
  registry.json
  <vertical_key>/
    metadata.json
    flow_base.json (si existe como base global del vertical)
    flow_base_scope_<scope_key>.json (si aplica)
    prompt_scope_<scope_key>.txt (si aplica)
    subflows/
      <scope_key>/
        <group_key>/
          <problem_key>.json
```

**Compat legacy (mientras se migra):**
- `subflow_scope_<scope>__<group>__<problem>.json` equivale a `subflows/<scope>/<group>/<problem>.json`.

## Contrato de `registry.json`
```json
{
  "<vertical_key>": { "label": "...", "archived": false, "path": "<vertical_key>" }
}
```

## Contrato de `metadata.json` (normativo mínimo)
```json
{
  "vertical_key": "...",
  "label": "...",
  "default_scope": "<scope_key>",
  "scopes": {
    "<scope_key>": {
      "label": "...",
      "flow_id": "<flow_id_or_filename>",
      "problem_groups": ["<group_key>", "..."],
      "archived": false
    }
  }
}
```

## Contrato de `flow_base_scope_*.json` (playbook)
```json
{
  "identity": { "role": "...", "tone": "..." },
  "goals": ["..."],
  "steps": [
    { "id": "welcome", "bot": "...", "input": null },
    { "id": "context", "bot": "...", "input": { "type": "text" } },
    { "id": "cta", "bot": "...", "options": ["..."], "routing": "..." }
  ],
  "rules": { "toggles": ["..."] }
}
```

## Contrato de problema (subflow)
```json
{
  "label": "...",
  "symptoms": ["..."],
  "questions": ["..."],
  "response": "...",
  "capture": ["..."]
}
```

## Reglas de seguridad operativa
1) La UI debe **ARCHIVAR** por defecto (soft delete). No borrar base files.  
2) “Eliminar definitivo” solo en modo avanzado y con doble confirmación.  
3) Nombres/keys deben ser slug-safe (sin espacios/acentos) para paths.  
4) No puede existir scope en metadata sin su flow correspondiente en disco.  
5) No puede existir subflow en disco que no esté referenciado por groups del scope (o debe marcarse como “orphan” en QA).

---

## Ejemplo completo: `home_services → fontaneria` (referencial)

**`registry.json` (snippet)**
```json
{
  "home_services": { "label": "Servicios para el Hogar", "archived": false, "path": "home_services" }
}
```

**`metadata.json` (snippet)**
```json
{
  "vertical_key": "home_services",
  "label": "Servicios para el Hogar",
  "default_scope": "fontaneria",
  "scopes": {
    "fontaneria": {
      "label": "Fontanería",
      "flow_id": "flow_base_scope_fontaneria.json",
      "problem_groups": ["problema"],
      "archived": false
    }
  }
}
```

**`flow_base_scope_fontaneria.json` (snippet)**
```json
{
  "identity": { "role": "Asesor de fontanería", "tone": "claro y resolutivo" },
  "goals": ["diagnosticar", "confirmar urgencia", "capturar datos", "agendar"],
  "steps": [
    { "id": "welcome", "bot": "Hola, soy el asistente de fontanería. ¿Qué problema tienes?" },
    { "id": "urgency", "bot": "¿Es una urgencia?", "options": ["Sí", "No"] },
    { "id": "location", "bot": "¿En qué ciudad estás?", "input": { "type": "text" } },
    { "id": "cta", "bot": "Podemos enviar un técnico hoy. ¿Agendamos?" }
  ],
  "rules": { "toggles": ["no_diagnosis_medica", "ask_permission_for_contact"] }
}
```

**`subflows/fontaneria/problema/fuga_grifo.json` (snippet)**
```json
{
  "label": "Fuga en grifo",
  "symptoms": ["goteo constante", "presión baja"],
  "questions": ["¿Desde cuándo ocurre?", "¿El grifo es nuevo?"],
  "response": "Podemos revisar juntas y recomendar la mejor solución.",
  "capture": ["contact_name", "contact_phone", "address"]
}
```
