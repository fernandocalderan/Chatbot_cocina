import pytest
from datetime import date

from app.models.ia_usage import IAUsage
from app.models.tenants import Tenant
from app.services.ia_usage_service import (
    IAQuotaExceeded,
    IAUsageService,
    PLAN_LIMITS_EUR,
)


from sqlalchemy.sql.functions import FunctionElement


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
        results = self._eval_entities()
        if len(results) == 1:
            return results[0]
        return tuple(results)

    def scalar(self):
        if not self.entities:
            return None
        results = self._eval_entities()
        return results[0] if results else None

    def _eval_entities(self):
        results = []
        for ent in self.entities:
            if isinstance(ent, FunctionElement):
                try:
                    target = list(ent.clauses)[0]
                    attr = getattr(target, "key", None)
                except Exception:
                    attr = None
                if not attr:
                    txt = str(ent)
                    if "tokens_out" in txt:
                        attr = "tokens_out"
                    elif "tokens_in" in txt:
                        attr = "tokens_in"
                    elif "cost_eur" in txt:
                        attr = "cost_eur"
                    elif self.data and hasattr(self.data[0], "cost_eur"):
                        attr = "cost_eur"
                if not attr:
                    results.append(0)
                else:
                    results.append(
                        sum(float(getattr(row, attr, 0) or 0) for row in self.data)
                    )
            else:
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


@pytest.fixture
def db():
    return _InMemorySession()


@pytest.fixture
def tenant_base():
    return Tenant(
        id="tenant-base",
        name="Test Base",
        plan="BASE",
        timezone="UTC",
    )


def test_estimate_cost_basic():
    cost = IAUsageService.estimate_cost(
        model="gpt-4.1",
        tokens_in=1000,
        tokens_out=2000,
    )
    assert cost > 0
    assert isinstance(cost, float)


def test_monthly_cost_aggregate(db, tenant_base):
    IAUsageService.record_usage(
        db,
        tenant_id=tenant_base.id,
        model="gpt-4.1",
        tokens_in=100,
        tokens_out=100,
        cost_eur=0.001,
    )
    IAUsageService.record_usage(
        db,
        tenant_id=tenant_base.id,
        model="gpt-4.1",
        tokens_in=200,
        tokens_out=200,
        cost_eur=0.002,
    )
    total = IAUsageService.monthly_cost(db, tenant_base.id)
    assert abs(total - 0.003) < 1e-6


def test_monthly_token_count(db, tenant_base):
    IAUsageService.record_usage(
        db,
        tenant_id=tenant_base.id,
        model="gpt-4.1",
        tokens_in=50,
        tokens_out=150,
        cost_eur=0.0,
    )
    stats = IAUsageService.monthly_token_count(db, tenant_base.id)
    assert stats["tokens_in"] == 50
    assert stats["tokens_out"] == 150


def test_enforce_quota_allows_under_limit(db, tenant_base):
    IAUsageService.enforce_quota(db, tenant_base, estimated_cost_next_call=0.1)


def test_enforce_quota_hard_limit(db, tenant_base):
    limit = PLAN_LIMITS_EUR["BASE"]
    IAUsageService.record_usage(
        db,
        tenant_id=tenant_base.id,
        model="gpt-4.1",
        tokens_in=10,
        tokens_out=10,
        cost_eur=limit * 0.999,
    )
    with pytest.raises(IAQuotaExceeded):
        IAUsageService.enforce_quota(
            db,
            tenant=tenant_base,
            estimated_cost_next_call=limit * 0.1,
        )
