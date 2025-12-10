import pytest
from datetime import date

from app.models.ia_usage import IAUsage
from app.models.tenants import Tenant
from app.services.ia_usage_service import IAQuotaExceeded, IAUsageService


class _Query:
    def __init__(self, data, entities=None):
        self.data = list(data)
        self.entities = entities or []

    def filter(self, *conds):
        filtered = self.data
        for cond in conds:
            left = getattr(cond, "left", None)
            right = getattr(cond, "right", None)
            key = getattr(left, "key", None)
            if key is None:
                continue
            val = getattr(right, "value", right)
            op = str(getattr(cond, "operator", "=="))
            if ">=" in op or "ge" in op:
                filtered = [row for row in filtered if getattr(row, key) >= val]
            else:
                filtered = [row for row in filtered if getattr(row, key) == val]
        return _Query(filtered, self.entities)

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return list(self.data)

    def first(self):
        if not self.entities:
            return (self.data + [None])[0]
        return self._eval_entities()[0]

    def scalar(self):
        if not self.entities:
            return None
        results = self._eval_entities()
        return results[0] if results else None

    def _eval_entities(self):
        results = []
        for ent in self.entities:
            if hasattr(ent, "clauses"):
                try:
                    target = list(ent.clauses)[0]
                    attr = getattr(target, "key", None)
                except Exception:
                    attr = None
                if attr:
                    results.append(
                        sum(float(getattr(row, attr, 0) or 0) for row in self.data)
                    )
                    continue
            results.append(ent)
        return results


class _InMemorySession:
    def __init__(self):
        self.ia_usages: list[IAUsage] = []

    def add(self, obj):
        if isinstance(obj, IAUsage):
            self.ia_usages.append(obj)

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        return None

    def query(self, *entities):
        if not entities:
            return _Query([])
        return _Query(self.ia_usages, entities=list(entities))


def _simulate_messages(total: int, limit_eur: float, tokens_in: int, tokens_out: int):
    db = _InMemorySession()
    tenant = Tenant(
        id="tenant-sim",
        name="Sim",
        plan="PRO",
        timezone="UTC",
        ia_enabled=True,
        use_ia=True,
        ia_monthly_limit_eur=limit_eur,
    )
    per_call_cost = IAUsageService.estimate_cost(
        "gpt-4.1-mini", tokens_in=tokens_in, tokens_out=tokens_out
    )
    calls = 0
    for i in range(total):
        try:
            IAUsageService.enforce_quota(
                db, tenant, estimated_cost_next_call=per_call_cost
            )
        except IAQuotaExceeded:
            break
        IAUsageService.record_usage(
            db,
            tenant_id=tenant.id,
            model="gpt-4.1-mini",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_eur=per_call_cost,
            session_id=f"session-{i}",
            call_type="reply",
            usage_date=date.today(),
        )
        calls += 1
    spent = IAUsageService.monthly_cost(db, tenant.id)
    return calls, spent, per_call_cost


def test_cost_stays_under_limit_for_200_messages():
    calls, spent, per_call_cost = _simulate_messages(
        total=200, limit_eur=25.0, tokens_in=120, tokens_out=80
    )
    assert calls == 200
    assert spent <= 25.0
    assert per_call_cost > 0


def test_provider_stops_after_quota_with_large_batch():
    calls, spent, per_call_cost = _simulate_messages(
        total=1000, limit_eur=1.0, tokens_in=8000, tokens_out=8000
    )
    assert calls < 1000
    assert calls > 0
    assert spent <= 1.0 + per_call_cost
    assert spent >= per_call_cost
