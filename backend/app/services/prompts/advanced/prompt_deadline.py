DEADLINE_ADVANCED = """
Determina la urgencia del proyecto del usuario.

Opciones oficiales:
- Alta (quiere empezar YA)
- Media (1–2 meses)
- Baja (3 meses o más)
- Exploratorio (solo mirando opciones)

Reglas:
- Si el usuario no responde con claridad, pregunta SOLO UNA VEZ.
- No presiones ni fuerces una decisión.

Formato:
{
 "question": "<texto o vacío>",
 "urgencia": "<clasificación>"
}

Texto:
"{user_text}"
"""
