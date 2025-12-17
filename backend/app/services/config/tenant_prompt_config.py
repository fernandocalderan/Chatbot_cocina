from typing import Any, Dict, Optional

from app.services.verticals import (
    fetch_tenant_vertical_key,
    vertical_prompt,
    vertical_prompt_extension,
)


def get_tenant_prompt_config(tenant_id: Optional[str]) -> Dict[str, Any]:
    """
    Devuelve la config IA del tenant.
    De momento es un stub con valores por defecto.
    Más adelante se puede enlazar a la tabla configs o a un JSON.
    """
    # Defaults conservadores
    base = {
        "ia": {
            "enabled": True,
            "model_primary": "gpt-4.1",
            "model_fallback": "gpt-4.1-mini",
            "tone": "profesional",
            "language_default": "es",
            "max_tokens": 650,
            "max_cost_month": 25.0,
        }
    }

    try:
        vertical_key = fetch_tenant_vertical_key(tenant_id)
        v_prompt = vertical_prompt(vertical_key)
        if v_prompt:
            ext = vertical_prompt_extension(vertical_key)
            base["vertical_prompt"] = f"{v_prompt}\n\n{ext}".strip() if ext else v_prompt
    except Exception:
        pass

    # Aquí podrías hacer lookup real por tenant_id
    # if tenant_id:
    #   cargar de DB / configs

    return base
