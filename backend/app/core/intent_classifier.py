import re
from typing import Optional


class IntentClassifier:
    """
    Stub determinista para extraer campos básicos sin IA.
    """

    def classify(self, text: str) -> dict:
        data: dict[str, Optional[str]] = {
            "urgency": None,
            "budget": None,
            "measures": None,
            "style": None,
        }

        # Urgency heuristics
        urgency_map = {
            "urgente": "urgente_30_dias",
            "prisa": "urgente_30_dias",
            "ya": "urgente_30_dias",
            "este año": "este_ano",
            "este trimestre": "este_trimestre",
            "3 meses": "este_trimestre",
        }
        lower = text.lower()
        for k, v in urgency_map.items():
            if k in lower:
                data["urgency"] = v
                break

        # Budget simple number/range detection
        m_budget = re.search(r"(\d{3,6})", text.replace(".", "").replace(",", ""))
        if m_budget:
            data["budget"] = m_budget.group(1)

        # Measures heuristic (e.g., 3x2, 3.20 x 2.40)
        m_measures = re.search(r"(\d+[.,]?\d*)\s*[xX]\s*(\d+[.,]?\d*)", text)
        if m_measures:
            data["measures"] = f"{m_measures.group(1)}x{m_measures.group(2)}"

        # Style hints
        styles = ["moderno", "minimalista", "rústico", "industrial", "clásico"]
        for s in styles:
            if s in lower:
                data["style"] = s
                break

        return {k: v for k, v in data.items() if v is not None}
