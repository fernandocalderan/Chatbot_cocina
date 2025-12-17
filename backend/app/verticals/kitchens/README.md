# Kitchens (v1.0 + v1.1)

## v1.0 (estructura)
- `flow_base.json`: flujo base (ejecutable por FlowEngine).
- `prompt_vertical.txt`: prompt vertical base (bloqueado).
- `semantic_schema.json`: semántica del lead.
- `kpi_defaults.json`: defaults de KPI/scoring.

## v1.1 (inteligencia percibida)
Sin cambiar estructura del flujo ni contratos del widget/API:
- Copy enriquecido por bloque vía `text_enriched` y variantes vía `text_variants` en `backend/app/flows/*`.
- Intervención IA contextual solo para sesiones `web_widget` y solo cuando hay texto libre/dudas/preguntas.
- Prompt adicional: `prompt_vertical_extension.txt` (se concatena al prompt vertical base en runtime).

### Umbrales (opcionales, por env var)
- `KITCHENS_ENRICHED_SCORE_THRESHOLD` (default `70`)
- `KITCHENS_ENRICHED_FRICTION_SECONDS` (default `12`)
