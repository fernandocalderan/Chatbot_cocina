STYLE_ADVANCED = """
Tu tarea es determinar el estilo deseado para el proyecto de cocina o mueble.

Estilos permitidos:
- Moderno
- Minimalista
- Nórdico
- Industrial
- Clásico
- Mediterráneo
- Rústico
- No definido

Reglas:
- No inventes. Si no sabes el estilo, pregunta.
- Si menciona palabras como "negro mate", "madera", "lineal", "sin tiradores", apunta siempre a un estilo compatible.
- Responde solo:
{
 "question": "<pregunta si falta algo>",
 "value": "<estilo>"
}

Texto:
"{user_text}"
"""
