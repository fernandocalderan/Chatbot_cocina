# QA manual · Verticals editor

## Preparación
- `cd /home/fernando/Escritorio/Chatbot_cocina/admin_panel`
- `source .venv/bin/activate`
- `streamlit run app.py --server.port 8502`

## Checklist click‑by‑click
1) Crear plantilla (wizard)
   - Clic en “+ Nuevo vertical”.
   - Paso 1: completar nombre + slug y avanzar.
   - Paso 2: añadir 1–2 especialidades, completar identidad/objetivos/guion/reglas.
   - Paso 3: añadir 1–2 problemas frecuentes y crear.
   - Verificar que aparece en el árbol.

2) Editar guion
   - Seleccionar plantilla → especialidad.
   - Editar “Identidad del experto” y guardar.
   - Modificar textos de 2 pasos y guardar.

3) Simulador
   - Clic en “Simulador”.
   - Avanzar por 2–3 pasos.
   - Reiniciar y verificar inicio correcto.

4) Problemas frecuentes
   - En panel derecho, crear un problema nuevo.
   - Editar síntomas/preguntas/CTA y guardar.
   - Eliminar un problema con confirmación.

5) Duplicar especialidad
   - En “Duplicar o eliminar”, duplicar especialidad con nuevo key.
   - Verificar que aparece en el árbol y tiene prompt/flow copiados.

6) Archivar plantilla
   - Clic en “Archivar plantilla”.
   - Verificar que desaparece del árbol (modo normal).
   - Activar “Mostrar opciones avanzadas” y comprobar que aparece con estado “Archivada”.

## Cierre
- `deactivate`
