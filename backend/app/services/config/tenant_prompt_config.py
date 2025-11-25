from typing import Dict, Any, Optional


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

    # Aquí podrías hacer lookup real por tenant_id
    # if tenant_id:
    #   cargar de DB / configs

    return base
