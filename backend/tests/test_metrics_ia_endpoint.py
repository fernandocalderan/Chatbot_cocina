import pytest
from fastapi.testclient import TestClient
from sqlalchemy.sql.functions import FunctionElement

from app.api.deps import get_db
from app.main import app
from app.models.ia_usage import IAUsage
from app.models.tenants import Tenant
from app.services.ia_usage_service import IAUsageService
from app.middleware.authz import AuthzContext, get_authz_context, require_any_role


class _Query:
    def __init__(self, data, entities=None):
        self.data = list(data)
        self.entities = entities or []
        self._offset = 0
        self._limit = None

    def filter(self, *conds):
        filtered = self.data
        for cond in conds:
            left = getattr(cond, "left", None)
            right = getattr(cond, "right", None)
            key = getattr(left, "key", None)
            val = getattr(right, "value", right)
            op = str(getattr(cond, "operator", "=="))
            if ">=" in op or "ge" in op:
                filtered = [row for row in filtered if getattr(row, key) >= val]
            else:
                filtered = [row for row in filtered if getattr(row, key) == val]
        return _Query(filtered, self.entities)

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, n):
        self._limit = n
        return self

    def all(self):
        end = None if self._limit is None else self._limit
        return self.data[:end]

    def scalar(self):
        if not self.entities:
            return None
        results = self._eval_entities()
        return results[0] if results else None

    def first(self):
        if not self.entities:
            return (self.data + [None])[0]
        results = self._eval_entities()
        if len(results) == 1:
            return results[0]
        return tuple(results)

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


class _MemorySession:
    def __init__(self):
        self.tenants: list[Tenant] = []
        self.usages: list[IAUsage] = []

    def add(self, obj):
        if isinstance(obj, Tenant):
            self.tenants.append(obj)
        if isinstance(obj, IAUsage):
            self.usages.append(obj)

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        return None

    def query(self, *entities):
        entities = list(entities) if entities else []
        dataset = (
            self.usages
            if any(isinstance(e, FunctionElement) or e is IAUsage for e in entities)
            else self.tenants
        )
        return _Query(dataset, entities=entities)


@pytest.fixture
def memory_db():
    return _MemorySession()


@pytest.fixture
def client(memory_db):
    # Override dependency to use in-memory session
    def override_get_db():
        try:
            yield memory_db
        finally:
            memory_db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_authz_context] = lambda: AuthzContext(
        tenant_id=None, user_id="test-admin", roles=["ADMIN"], token_type="access"
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_metrics_ia_endpoint_basic(memory_db, client: TestClient):
    tenant = Tenant(
        id="tenant-metrics",
        name="Tenant Metrics",
        plan="BASE",
        timezone="UTC",
    )
    memory_db.add(tenant)
    memory_db.commit()

    IAUsageService.record_usage(
        memory_db,
        tenant_id=tenant.id,
        model="gpt-4.1",
        tokens_in=500,
        tokens_out=500,
        cost_eur=0.0015,
    )

    res = client.get(
        f"/v1/metrics/ia/tenant/{tenant.id}",
        headers={"X-Api-Key": "test"},
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["tenant_id"] == tenant.id
    assert "monthly" in payload
    assert "latest" in payload
    assert payload["monthly"]["total_cost_eur"] >= 0
