import os
import json
from typing import Optional, Dict, Any

from openai import OpenAI

from app.interfaces.ai_provider import AiProvider
from app.services.prompts.router.prompt_router import PromptRouter
from app.services.config.tenant_prompt_config import get_tenant_prompt_config


class OpenAIService(AiProvider):
    """
    Implementación de proveedor IA basada en OpenAI,
    con soporte para:
    - prompts avanzados por flujo (PromptRouter)
    - configuración por tenant (tenant_prompt_config)
    - modelo primario / fallback (stub para control de costes)
    """

    def __init__(self):
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise Exception("OPENAI_API_KEY missing")
        self.client = OpenAI(api_key=key)

    # ---------- Helpers internos ----------

    def _resolve_models(self, tenant_id: Optional[str]) -> Dict[str, str]:
        cfg = get_tenant_prompt_config(tenant_id)
        ia_cfg = cfg.get("ia", {})
        primary = ia_cfg.get("model_primary", "gpt-4.1")
        fallback = ia_cfg.get("model_fallback", "gpt-4.1-mini")
        return {"primary": primary, "fallback": fallback}

    # En el futuro aquí puedes inyectar lógica real de coste/uso
    def _should_use_fallback(self, tenant_id: Optional[str]) -> bool:
        # Stub: siempre false por ahora
        return False

    # ---------- API pública (extract / summary / reply) ----------

    async def extract_fields(
        self,
        text: str,
        purpose: str = "extraction",
        tenant_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extrae campos estructurados según el propósito.
        purpose:
        - project_type
        - style
        - dimensions
        - budget
        - urgency
        - extraction (multi-campo genérico)
        """
        models = self._resolve_models(tenant_id)
        use_fallback = self._should_use_fallback(tenant_id)
        model = models["fallback"] if use_fallback else "gpt-4.1-mini"

        prompt = PromptRouter.get_extraction_prompt(
            purpose=purpose,
            user_text=text,
            language=language,
            tenant_config=get_tenant_prompt_config(tenant_id),
        )

        completion = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[{"role": "system", "content": prompt}],
        )

        content = completion.choices[0].message.content

        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("JSON no es dict")
            return data
        except Exception:
            # Fallback estructural mínimo
            return {
                "raw": content,
                "error": "parse_error",
            }

    async def generate_summary(
        self,
        lead_data: Dict[str, Any],
        tenant_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Genera un resumen comercial corto para un lead.
        Usa prompt de tipo 'summary' vía PromptRouter.
        """
        models = self._resolve_models(tenant_id)
        use_fallback = self._should_use_fallback(tenant_id)
        model = models["primary"] if not use_fallback else models["fallback"]

        prompt = PromptRouter.get_generation_prompt(
            purpose="summary",
            payload=lead_data,
            language=language,
            tenant_config=get_tenant_prompt_config(tenant_id),
        )

        completion = self.client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[{"role": "system", "content": prompt}],
        )

        return completion.choices[0].message.content

    async def generate_reply(
        self,
        message: str,
        context: Dict[str, Any],
        purpose: str = "reply_contextual",
        tenant_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Genera una respuesta conversacional:
        - reply_contextual (por defecto)
        - welcome
        - closing
        - microproposal
        """
        models = self._resolve_models(tenant_id)
        use_fallback = self._should_use_fallback(tenant_id)

        if purpose in ("welcome", "closing", "microproposal"):
            model = models["primary"] if not use_fallback else models["fallback"]
        else:
            # reply contextual puede ir con fallback o modelo económico
            model = models["fallback"] if use_fallback else models["primary"]

        payload = {
            "message": message,
            "context": context,
        }

        prompt = PromptRouter.get_generation_prompt(
            purpose=purpose,
            payload=payload,
            language=language,
            tenant_config=get_tenant_prompt_config(tenant_id),
        )

        completion = self.client.chat.completions.create(
            model=model,
            temperature=0.4,
            messages=[{"role": "system", "content": prompt}],
        )

        return completion.choices[0].message.content
