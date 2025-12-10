import os
from typing import Dict, Tuple, Optional

from openai import OpenAI


class AIClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, use_ai: bool = True):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("AI_MODEL", "gpt-4.1-mini")
        self.use_ai = bool(use_ai)
        self.client = (
            OpenAI(api_key=self.api_key) if self.api_key and self.use_ai else None
        )

    def generate_commercial_brief(self, lead_data: Dict, prompt_text: Optional[str] = None) -> Tuple[str, int, int]:
        """
        Llama a OpenAI para generar un breve resumen comercial.
        Devuelve texto, tokens_in, tokens_out.
        """
        if not self.client or not self.api_key or not self.use_ai:
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

    def generate_text_snippet(self, kind: str, vars_data: Dict) -> Tuple[str, int, int]:
        """
        Genera textos cortos (welcome, closing, micro_proposal) con OpenAI.
        Devuelve texto, tokens_in, tokens_out. Fallback determinista si no hay API.
        """
        if not self.client or not self.api_key or not self.use_ai:
            return self._deterministic_snippet(kind, vars_data), 0, 0

        system_prompts = {
            "welcome": "Eres un asistente amable de una tienda de cocinas/muebles. Redacta un saludo breve, cálido y profesional.",
            "closing": "Eres un asistente amable. Redacta un cierre corto invitando a seguir en contacto.",
            "micro_proposal": "Eres un consultor de cocinas/muebles. Genera una micro-propuesta de 3-4 líneas con próxima acción.",
        }
        user_prompt = self._build_prompt(vars_data)
        system_msg = system_prompts.get(kind, system_prompts["welcome"])
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=120,
                temperature=0.5,
            )
            text = resp.choices[0].message.content
            usage = resp.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            return text, tokens_in, tokens_out
        except Exception:
            return self._deterministic_snippet(kind, vars_data), 0, 0

    def _deterministic_snippet(self, kind: str, data: Dict) -> str:
        name = data.get("contact_name") or "allí"
        if kind == "closing":
            return f"Gracias por tu tiempo, {name}. Te contactaremos para seguir afinando tu proyecto."
        if kind == "micro_proposal":
            base = self._deterministic_brief(data)
            return f"{base} Próximo paso: agendar una llamada breve para confirmar requisitos."
        return "Hola, soy tu asistente para proyectos a medida. Te ayudaré a recoger los datos clave y preparar una propuesta inicial."
