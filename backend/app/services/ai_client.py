import os
from typing import Dict, Tuple, Optional

from openai import OpenAI


class AIClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("AI_MODEL", "gpt-4.1-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_commercial_brief(self, lead_data: Dict, prompt_text: Optional[str] = None) -> Tuple[str, int, int]:
        """
        Llama a OpenAI para generar un breve resumen comercial.
        Devuelve texto, tokens_in, tokens_out.
        """
        if not self.client or not self.api_key:
            brief = self._deterministic_brief(lead_data)
            return brief, 0, 0

        prompt = prompt_text or self._build_prompt(lead_data)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente de ventas de cocinas y muebles a medida. Redacta breve, claro y orientado a acción."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=180,
                temperature=0.4,
            )
            text = resp.choices[0].message.content
            usage = resp.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            return text, tokens_in, tokens_out
        except Exception:
            brief = self._deterministic_brief(lead_data)
            return brief, 0, 0

    def _build_prompt(self, data: Dict) -> str:
        def get(k): return data.get(k) or "N/D"

        return (
            "Genera un briefing comercial corto (5-6 líneas) para un proyecto de cocinas/muebles a medida:\n"
            f"- Tipo de proyecto: {get('project_type')}\n"
            f"- Medidas: {get('measures')}\n"
            f"- Estilo: {get('style')}\n"
            f"- Presupuesto: {get('budget')}\n"
            f"- Urgencia: {get('urgency')}\n"
            f"- Ubicación: {get('location')}\n"
            f"- Canal preferido: {get('preferred_channel')}\n"
            "Incluye recomendación breve y próximo paso sugerido."
        )

    def _deterministic_brief(self, data: Dict) -> str:
        pieces = []
        if data.get("project_type"):
            pieces.append(f"Proyecto: {data['project_type']}.")
        if data.get("measures"):
            pieces.append(f"Medidas aprox: {data['measures']}.")
        if data.get("style"):
            pieces.append(f"Estilo: {data['style']}.")
        if data.get("budget"):
            pieces.append(f"Presupuesto: {data['budget']}.")
        if data.get("urgency"):
            pieces.append(f"Urgencia: {data['urgency']}.")
        if data.get("location"):
            pieces.append(f"Ubicación: {data['location']}.")
        if data.get("preferred_channel"):
            pieces.append(f"Contacto por: {data['preferred_channel']}.")
        pieces.append("Recomendación: agendar llamada y compartir moodboard inicial.")
        return " ".join(pieces)
