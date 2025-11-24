import json
from typing import Any, Optional

from openai import OpenAI, OpenAIError
from loguru import logger


class AIExtractor:
    def __init__(self, api_key: Optional[str], model: str = "gpt-4.1-mini"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None

    def extract(self, text: str) -> dict[str, Any]:
        if not self.client or not self.api_key:
            return {}
        prompt = (
            "Extrae estilo, medidas, presupuesto y urgencia de este texto libre. "
            "Devuelve JSON con campos: style (string), measures (string), "
            "budget (string, rango o cifra), urgency (uno de: sin_prisa, este_ano, este_trimestre, urgente_30_dias). "
            "Responde siempre en JSON estricto."
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
            data = json.loads(content)
            result: dict[str, Any] = {}
            if isinstance(data, dict):
                for key in ("style", "measures", "budget", "urgency"):
                    val = data.get(key)
                    if val:
                        result[key] = str(val)
            return result
        except (OpenAIError, json.JSONDecodeError, IndexError, KeyError) as exc:
            logger.warning({"event": "ai_extract_failed", "error": str(exc)})
            return {}
