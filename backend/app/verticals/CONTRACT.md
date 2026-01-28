# Contrato V2 · Editor profesional de conversaciones

## Fuente de verdad (source of truth)
- **Edición**: el panel administra *plantillas* en filesystem (`backend/app/verticals/*`).
- **Runtime**: los tenants ejecutan flows publicados en DB; si no hay publicación, el runtime usa el flow base del vertical/scope.

## Definiciones
- **Vertical (dominio)** → **Scope (especialidad)** → **Flow (playbook conversacional)** → **Subflows (problem packs / caminos)**.

## Principio clave
**“Flow NO es un grafo técnico; es un Playbook conversacional editable en bloques humanos (Identidad/Objetivos/Guion/Reglas).”**

---

## Layout de filesystem esperado (normativo)
```
backend/app/verticals/
  registry.json
  <vertical_key>/
    metadata.json
    flow_base.json
    flow_base_scope_<scope_key>.json
    prompt_scope_<scope_key>.txt
    subflows/
      <scope_key>/
        <group_key>/
          <problem_key>.json
```

### Legacy (aceptado mientras migramos)
- `subflow_scope_<scope>__<group>__<problem>.json` en la raíz del vertical.
- `flow_scope_<scope>.json` como equivalente legacy de `flow_base_scope_<scope>.json`.

---

## Contrato de `registry.json`
```json
{
  "<vertical_key>": {
    "label": "Nombre visible",
    "archived": false,
    "path": "<vertical_key>"
  }
}
```

## Contrato de `metadata.json` (mínimo normativo)
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

---

## Contrato V2 de Flow (Playbook conversacional por scope)
```json
{
  "identity": {
    "role": "Asesor experto",
    "tone": "claro, empático",
    "do_dont": ["haz preguntas concretas", "no diagnostiques sin datos"]
  },
  "objectives": ["diagnosticar", "proponer siguiente paso", "capturar datos"],
  "slots_to_capture": ["contact_name", "contact_phone", "address"],
  "steps": [
    {
      "id": "welcome",
      "bot": "Hola, ¿te puedo hacer 3 preguntas rápidas?",
      "input": null
    },
    {
      "id": "urgency",
      "bot": "¿Qué tan urgente es?",
      "options": ["Alta", "Media", "Baja"],
      "save_to": "urgency"
    }
  ],
  "rules_toggles": ["no_diagnosis_medica", "ask_permission_for_contact"],
  "fallbacks": {
    "fallback_clarify": "No me quedó claro. ¿Puedes concretarlo un poco más?",
    "fallback_summary_and_confirm": "Resumen: ... ¿es correcto?"
  },
  "handoff": {
    "enabled": true,
    "channels": ["whatsapp", "email", "phone"]
  },
  "languages": {
    "default": "es",
    "available": ["es", "ca", "pt", "en"]
  }
}
```

---

## Contrato V2 de Subflow (Problem Pack)
```json
{
  "label": "Fuga en grifo",
  "group": "problema",
  "intent_tags": ["fuga", "grifo"],
  "symptoms": ["goteo constante", "presión baja"],
  "key_questions": ["¿Desde cuándo ocurre?", "¿El grifo es nuevo?"],
  "safe_guidance": ["Cierra la llave de paso si hay fuga intensa"],
  "cta": "¿Quieres que agendemos una visita técnica?",
  "capture_fields": ["contact_name", "contact_phone", "address"],
  "examples": ["Gotea el grifo de la cocina desde hace 2 días"]
}
```

---

## Reglas de seguridad operativa
1) UI debe **ARCHIVAR** por defecto (soft delete). No borrar base files.  
2) “Eliminar definitivo” solo en modo avanzado y con doble confirmación.  
3) Nombres/keys deben ser slug-safe (sin espacios/acentos) para paths.  
4) No puede existir scope en metadata sin su flow correspondiente en disco.  
5) No puede existir subflow en disco que no esté referenciado por groups del scope (o debe marcarse como “orphan” en QA).  

## MIGRATION warnings (QA)
- Si `metadata.scopes` no existe, el validador emite:  
  **“MIGRATION: metadata missing scopes V2 (legacy válido, pero no editable en modo profesional hasta migrar a scopes V2)”**  
- Este warning **no rompe** `--strict`, pero deja constancia para migración controlada.
- Si `registry.json` está incompleto (faltan `path` / `archived`) en verticales legacy, se reporta como **MIGRATION** (no error).
