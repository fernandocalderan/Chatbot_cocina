from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from app.core.config import get_settings
from app.services.pricing import get_plan_limits


@dataclass
class BudgetUsage:
    hour_key: str = ""
    day_key: str = ""
    month_key: str = ""
    hour_cost: float = 0.0
    day_cost: float = 0.0
    month_cost: float = 0.0

    def as_dict(self) -> dict:
        return {
            "hour": self.hour_cost,
            "day": self.day_cost,
            "month": self.month_cost,
        }


class BudgetManager:
    """
    Control de coste IA por tenant.
    Calcula buckets horario/diario/mensual en memoria.
    """

    LIMITS_EUR: Dict[str, float] = {"base": 10.0, "pro": 25.0, "elite": 100.0}

    def __init__(self, price_per_token: Optional[float] = None):
        settings = get_settings()
        self.price_per_token = float(
            price_per_token
            if price_per_token is not None
            else settings.ai_price_per_token_usd
        )
        self._usage: Dict[str, BudgetUsage] = {}

    def _keys(self, now: datetime) -> tuple[str, str, str]:
        return now.strftime("%Y%m%d%H"), now.strftime("%Y%m%d"), now.strftime("%Y%m")

    def _reset_if_needed(self, tenant_id: str, now: datetime) -> BudgetUsage:
        usage = self._usage.setdefault(tenant_id, BudgetUsage())
        hour_key, day_key, month_key = self._keys(now)
        if usage.hour_key != hour_key:
            usage.hour_key = hour_key
            usage.hour_cost = 0.0
        if usage.day_key != day_key:
            usage.day_key = day_key
            usage.day_cost = 0.0
        if usage.month_key != month_key:
            usage.month_key = month_key
            usage.month_cost = 0.0
        return usage

    def get_limit(self, plan: str) -> float:
        limits = get_plan_limits(plan)
        max_cost = limits.get("max_ia_cost")
        if max_cost is not None:
            return float(max_cost)
        return self.LIMITS_EUR.get(plan, self.LIMITS_EUR["base"])

    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        return (tokens_in + tokens_out) * self.price_per_token

    def is_allowed(
        self,
        tenant_id: str,
        plan: str,
        projected_cost: float = 0.0,
        now: Optional[datetime] = None,
    ) -> dict:
        now = now or datetime.utcnow()
        usage = self._reset_if_needed(tenant_id, now)
        limit = self.get_limit(plan)
        allowed = (usage.month_cost + projected_cost) <= limit
        return {
            "allowed": allowed,
            "limit": limit,
            "usage": usage.as_dict(),
            "plan": plan,
        }

    def register(
        self,
        tenant_id: str,
        plan: str,
        tokens_in: int,
        tokens_out: int,
        now: Optional[datetime] = None,
    ) -> dict:
        now = now or datetime.utcnow()
        usage = self._reset_if_needed(tenant_id, now)
        cost = (tokens_in + tokens_out) * self.price_per_token
        usage.hour_cost += cost
        usage.day_cost += cost
        usage.month_cost += cost
        return {
            "cost": cost,
            "usage": usage.as_dict(),
            "limit": self.get_limit(plan),
            "plan": plan,
        }
