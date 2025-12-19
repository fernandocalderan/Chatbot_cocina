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

    @staticmethod
    def _apply_vertical_prompt(prompt: str, tenant_config: Optional[Dict[str, Any]]) -> str:
        if not tenant_config:
            return prompt
        vertical_prompt = tenant_config.get("vertical_prompt")
        vp = str(vertical_prompt).strip() if vertical_prompt else ""
        knowledge = tenant_config.get("knowledge_base")
        kb = str(knowledge).strip() if knowledge else ""
        prefix_parts: list[str] = []
        if vp:
            prefix_parts.append(vp)
        if kb:
            prefix_parts.append("Materiales del negocio (archivos cargados):\n" + kb)
        if not prefix_parts:
            return prompt
        return f"{'\n\n'.join(prefix_parts)}\n\n{prompt}"

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
            return cls._apply_vertical_prompt(PROJECT_TYPE_ADVANCED.format(user_text=user_text), tenant_config)

        if purpose == "style":
            return cls._apply_vertical_prompt(STYLE_ADVANCED.format(user_text=user_text), tenant_config)

        if purpose == "dimensions":
            return cls._apply_vertical_prompt(DIMENSIONS_ADVANCED.format(user_text=user_text), tenant_config)

        if purpose == "budget":
            return cls._apply_vertical_prompt(BUDGET_ADVANCED.format(user_text=user_text), tenant_config)

        if purpose == "urgency":
            return cls._apply_vertical_prompt(DEADLINE_ADVANCED.format(user_text=user_text), tenant_config)

        # Genérico extractor multi-campo
        return cls._apply_vertical_prompt(EXTRACTION_PROMPT.format(user_text=user_text), tenant_config)

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
            return cls._apply_vertical_prompt(WELCOME_ADVANCED, tenant_config)

        if purpose == "closing":
            return cls._apply_vertical_prompt(CLOSING_ADVANCED, tenant_config)

        if purpose == "microproposal":
            return cls._apply_vertical_prompt(MICROPROPOSAL_ADVANCED.format(lead_data=payload), tenant_config)

        if purpose == "summary":
            # Reutiliza el SUMMARY_PROMPT básico
            import json
            return cls._apply_vertical_prompt(SUMMARY_PROMPT.format(data=json.dumps(payload, ensure_ascii=False)), tenant_config)

        if purpose == "reply_contextual":
            user_message = payload.get("message", "")
            context = payload.get("context", {})
            import json
            return cls._apply_vertical_prompt(REPLY_CONTEXTUAL_ADVANCED.format(
                user_message=user_message,
                context=json.dumps(context, ensure_ascii=False),
            ), tenant_config)

        if purpose == "custom_prompt":
            return cls._apply_vertical_prompt(payload.get("prompt") or "", tenant_config)

        # Fallback: reply básico
        message = payload.get("message", "")
        context = payload.get("context", {})
        import json
        base = REPLY_PROMPT.format(
            message=message,
            contexto=json.dumps(context, ensure_ascii=False),
        )
        return cls._apply_vertical_prompt(base, tenant_config)
