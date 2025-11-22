from typing import Dict, Tuple


def compute_score(session_state: dict, scoring_config: dict) -> Tuple[int, dict]:
    """
    Calcula score 0-100 y breakdown basado en pesos y mappings del flow.
    """
    vars_data = session_state.get("vars", {})
    weights = scoring_config.get("weights", {})
    mappings = scoring_config.get("mappings", {})

    def get_weight(key: str) -> int:
        return weights.get(key, 0)

    breakdown = {}
    total_weight = sum(weights.values()) or 1
    weighted_sum = 0

    def add_component(name: str, raw_score: int):
        nonlocal weighted_sum
        w = get_weight(name)
        breakdown[name] = {"score": raw_score, "weight": w}
        weighted_sum += raw_score * w

    # budget: si existe, dar 70; si no, 0
    budget_score = 70 if vars_data.get("budget") else 0
    add_component("budget", budget_score)

    # urgency mapping
    urgency_value = vars_data.get("urgency")
    urgency_map = mappings.get("urgency", {}).get("es", {})
    urgency_score = urgency_map.get(urgency_value, 50 if urgency_value else 0)
    add_component("urgency", urgency_score)

    # area_m2: si hay measures, asignar 60
    area_score = 60 if vars_data.get("measures") else 0
    add_component("area_m2", area_score)

    # style_defined: si hay style, 80
    style_score = 80 if vars_data.get("style") else 0
    add_component("style_defined", style_score)

    # origin: si hay origin, 50
    origin_score = 50 if vars_data.get("origin") else 0
    add_component("origin", origin_score)

    score = round(weighted_sum / total_weight) if total_weight else 0
    return score, breakdown
