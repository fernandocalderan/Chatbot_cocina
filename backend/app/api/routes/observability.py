from fastapi import APIRouter, HTTPException, status

from app.observability.metrics import get_registry
from app.observability.slo import get_slo_status

router = APIRouter(prefix="/observability", tags=["observability"])


def _summary_for_tenant(tenant_id: str | None = None):
    registry = get_registry()
    api_total = 0.0
    ia_total = 0.0
    for key, val in registry.counters.get("api_requests_total", {}).items():
        labels = dict(key)
        if tenant_id and labels.get("tenant_id") != tenant_id:
            continue
        api_total += val
    for key, val in registry.counters.get("ia_requests_total", {}).items():
        labels = dict(key)
        if tenant_id and labels.get("tenant_id") != tenant_id:
            continue
        ia_total += val
    summary = {
        "api_requests_total": api_total,
        "ia_requests_total": ia_total,
        "slo": get_slo_status(),
    }
    return summary


@router.get("/metrics/summary")
def metrics_summary():
    return _summary_for_tenant()


@router.get("/metrics/tenant/{tenant_id}")
def metrics_summary_tenant(tenant_id: str):
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_tenant")
    return _summary_for_tenant(tenant_id)


@router.get("/slo/status")
def slo_status():
    return get_slo_status()
