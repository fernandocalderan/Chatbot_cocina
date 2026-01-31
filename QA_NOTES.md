# QA Panel de Flows v1 — Resultados
Fecha: 2026-01-31 13:03:51 CET
Entorno: local (CLI sin navegador/GUI)
Commit/branch: 65fe64f / feat/verticals-cockpit

## Resumen
- Total checks: 10
- OK: 0
- KO: 10

## Detalle por sección
- A) Sidebar: KO — No se pudo abrir UI (sin navegador en este entorno).
- B) Vertical: KO — No se pudo ejecutar creación (sin UI).
- C) Scope: KO — No se pudo ejecutar creación (sin UI).
- D) Gating: KO — No se pudo validar (sin UI).
- E) Checklist semáforo: KO — No se pudo validar (sin UI).
- F) Flow base: KO — No se pudo validar (sin UI).
- G) Subflows: KO — No se pudo validar (sin UI).
- H) Selección automática: KO — No se pudo validar (sin UI).
- I) Tenants: KO — No se pudo validar (sin UI).
- J) Modo técnico: KO — No se pudo validar (sin UI).

## Incidencias
- ID: QA-01
  - Paso donde falla: Preparación (run del panel)
  - Cómo reproducir: `./scripts/run_admin_panel_local.sh`
  - Resultado esperado: Streamlit inicia en http://localhost:8502
  - Resultado actual: `Port 8502 is already in use`
  - Extracto log:
    - 2026-01-31 13:03:37.743 Port 8502 is already in use
  - Severidad: media (bloquea QA local hasta liberar puerto)

## Sugerencias de micro-fix
- Verificar si ya hay un panel corriendo en 8502 y cerrarlo, o exportar `PORT=8503` antes de ejecutar el script.

## Evidencias
- Log de arranque: `.qa_artifacts/streamlit.log`

## Notas
- No se pudo realizar QA manual completo porque este entorno no dispone de navegador/GUI para operar Streamlit.
