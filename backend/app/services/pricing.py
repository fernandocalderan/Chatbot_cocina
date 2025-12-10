"""
pricing.py
==========

Tabla centralizada de precios oficiales de modelos OpenAI.
Valores expresados por millón de tokens y convertidos a EUR mediante
un factor de conversión configurable.

Este módulo es la base futura para:
- Facturación
- IA Budget Settings
- Cost Forecasting
"""

USD_TO_EUR = 0.95  # factor conservador, ajustable en el futuro

# Precios oficiales por millón de tokens (USD)
MODEL_PRICING = {
    "gpt-4.1": {
        "input_usd_per_million": 5.0,
        "output_usd_per_million": 15.0,
    },
    "gpt-4.1-mini": {
        "input_usd_per_million": 0.6,
        "output_usd_per_million": 1.2,
    },
    "gpt-4.1-preview": {
        "input_usd_per_million": 4.0,
        "output_usd_per_million": 10.0,
    },
}


def normalize_model_name(model: str) -> str:
    """
    Normaliza el nombre del modelo a una clave estándar.
    Si no existe, se devuelve 'gpt-4.1' como fallback.
    """
    m = model.lower()

    if "gpt-4.1-mini" in m:
        return "gpt-4.1-mini"
    if "preview" in m or "gpt-4.1-preview" in m:
        return "gpt-4.1-preview"
    return "gpt-4.1"  # fallback seguro


def estimate_cost_eur(model: str, tokens_in: int, tokens_out: int) -> float:
    """
    Estima el coste en EUR para una llamada:
      - tokens_in → precio input
      - tokens_out → precio output
      - conversión USD→EUR

    Retorna float en EUR.
    """
    key = normalize_model_name(model)
    pricing = MODEL_PRICING.get(key, MODEL_PRICING["gpt-4.1"])

    usd_in = pricing["input_usd_per_million"] * (tokens_in / 1_000_000)
    usd_out = pricing["output_usd_per_million"] * (tokens_out / 1_000_000)

    total_usd = usd_in + usd_out
    total_eur = total_usd * USD_TO_EUR

    return float(total_eur)


# ----------------------------
# Planes y límites SaaS
# ----------------------------

PLAN_LIMITS = {
    "BASE": {
        "max_ia_cost": 0.0,  # IA deshabilitada en Base
        "max_sessions": 200,
        "features": {
            "ia_enabled": False,
            "billing_portal": True,
        },
    },
    "PRO": {
        "max_ia_cost": 25.0,
        "max_sessions": 2000,
        "features": {
            "ia_enabled": True,
            "billing_portal": True,
        },
    },
    "ELITE": {
        "max_ia_cost": 100.0,
        "max_sessions": 10000,
        "features": {
            "ia_enabled": True,
            "billing_portal": True,
        },
    },
}


def get_plan_limits(plan: str | None) -> dict:
    """
    Devuelve límites y features del plan normalizados (BASE/PRO/ELITE).
    """
    key = (plan or "BASE").upper()
    return PLAN_LIMITS.get(key, PLAN_LIMITS["BASE"])
