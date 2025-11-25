from typing import Optional, Dict, Any

from app.services.prompts.prompts_extraction import EXTRACTION_PROMPT
from app.services.prompts.prompts_summary import SUMMARY_PROMPT
from app.services.prompts.prompts_reply import REPLY_PROMPT

from app.services.prompts.advanced.prompt_welcome import WELCOME_ADVANCED
from app.services.prompts.advanced.prompt_project_type import PROJECT_TYPE_ADVANCED
from app.services.prompts.advanced.prompt_style import STYLE_ADVANCED
from app.services.prompts.advanced.prompt_dimensions import DIMENSIONS_ADVANCED
from app.services.prompts.advanced.prompt_budget import BUDGET_ADVANCED
from app.services.prompts.advanced.prompt_deadline import DEADLINE_ADVANCED
from app.services.prompts.advanced.prompt_closing import CLOSING_ADVANCED
from app.services.prompts.advanced.prompt_microproposal import MICROPROPOSAL_ADVANCED
from app.services.prompts.advanced.prompt_reply_contextual import REPLY_CONTEXTUAL_ADVANCED


class PromptRouter:
    """
    Router central de prompts IA.
    Decide qué prompt usar según:
    - propósito (purpose)
    - tenant_config (cuando lo tengas)
    - idioma (language)
    """

    @staticmethod
    def _normalize_language(language: Optional[str]) -> str:
        if not language:
            return "es"
        language = language.lower()
        if language.startswith("es"):
            return "es"
        if language.startswith("ca"):
            return "ca"
        if language.startswith("pt"):
            return "pt"
        if language.startswith("en"):
            return "en"
        return "es"

    # ---------- EXTRACCIÓN ESTRUCTURADA ----------

    @classmethod
    def get_extraction_prompt(
        cls,
        purpose: str,
        user_text: str,
        language: Optional[str] = None,
        tenant_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Devuelve el prompt adecuado para tareas de extracción:
        - project_type
        - style
        - dimensions
        - budget
        - urgency
        - default -> EXTRACTION_PROMPT genérico
        """
        _ = cls._normalize_language(language)

        if purpose == "project_type":
            return PROJECT_TYPE_ADVANCED.format(user_text=user_text)

        if purpose == "style":
            return STYLE_ADVANCED.format(user_text=user_text)

        if purpose == "dimensions":
            return DIMENSIONS_ADVANCED.format(user_text=user_text)

        if purpose == "budget":
            return BUDGET_ADVANCED.format(user_text=user_text)

        if purpose == "urgency":
            return DEADLINE_ADVANCED.format(user_text=user_text)

        # Genérico extractor multi-campo
        return EXTRACTION_PROMPT.format(user_text=user_text)

    # ---------- GENERACIÓN DE TEXTO ----------

    @classmethod
    def get_generation_prompt(
        cls,
        purpose: str,
        payload: Dict[str, Any],
        language: Optional[str] = None,
        tenant_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Devuelve el prompt adecuado para tareas generativas:
        - welcome
        - closing
        - microproposal
        - summary
        - reply_contextual
        """
        _ = cls._normalize_language(language)

        if purpose == "welcome":
            # No necesita payload específico
            return WELCOME_ADVANCED

        if purpose == "closing":
            return CLOSING_ADVANCED

        if purpose == "microproposal":
            return MICROPROPOSAL_ADVANCED.format(lead_data=payload)

        if purpose == "summary":
            # Reutiliza el SUMMARY_PROMPT básico
            import json
            return SUMMARY_PROMPT.format(data=json.dumps(payload, ensure_ascii=False))

        if purpose == "reply_contextual":
            user_message = payload.get("message", "")
            context = payload.get("context", {})
            import json
            return REPLY_CONTEXTUAL_ADVANCED.format(
                user_message=user_message,
                context=json.dumps(context, ensure_ascii=False),
            )

        if purpose == "custom_prompt":
            return payload.get("prompt") or ""

        # Fallback: reply básico
        message = payload.get("message", "")
        context = payload.get("context", {})
        import json
        base = REPLY_PROMPT.format(
            message=message,
            contexto=json.dumps(context, ensure_ascii=False),
        )
        return base
