import csv
import io
from fastapi import APIRouter, Depends, Response

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.tenants import Tenant
from app.middleware.authz import require_any_role
from app.services.ia_usage_service import IAUsageService
from app.services.quota_service import QuotaService
from app.observability import metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/ai", dependencies=[Depends(require_auth)])
def ai_metrics(db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        return {}
    quota_status = QuotaService.evaluate(db, t)
    return {
        "tenant_id": str(t.id),
        "ai_cost": t.ai_cost,
        "ai_monthly_limit": t.ai_monthly_limit,
        "usage_mode": getattr(t, "usage_mode", None),
        "needs_upgrade_notice": bool(getattr(t, "needs_upgrade_notice", False)),
        "quota_status": quota_status.to_dict() if quota_status else None,
    }


@router.get(
    "/ia/usage",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def ia_usage(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    usages = IAUsageService.get_monthly_usage(db, tenant_id)
    total_cost = IAUsageService.total_monthly_cost(db, tenant_id)
    return {
        "tenant_id": tenant_id,
        "entries": [
            {
                "date": str(u.date),
                "model": u.model,
                "tokens_in": u.tokens_in,
                "tokens_out": u.tokens_out,
                "cost_eur": float(u.cost_eur),
            }
            for u in usages
        ],
        "total_cost_eur": total_cost,
    }


@router.get(
    "/ia/usage.csv",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def ia_usage_csv(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    usages = IAUsageService.get_monthly_usage(db, tenant_id)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "model", "tokens_in", "tokens_out", "cost_eur"])
    for u in usages:
        writer.writerow(
            [
                str(u.date),
                u.model,
                u.tokens_in,
                u.tokens_out,
                float(u.cost_eur),
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="ia_usage.csv"'},
    )


@router.get(
    "/quota",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def quota_status(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        return {"tenant_id": tenant_id, "quota_status": None}
    status_snapshot = QuotaService.evaluate(db, tenant)
    return {
        "tenant_id": tenant_id,
        "quota_status": status_snapshot.to_dict(),
    }


@router.get(
    "/kpis",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def tenant_kpis(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        return {"tenant_id": tenant_id, "kpis": {}}
    quota = QuotaService.evaluate(db, tenant)
    tokens = IAUsageService.monthly_token_count(db, tenant_id)
    return {
        "tenant_id": tenant_id,
        "kpis": {
            "usage_mode": quota.mode.value if quota else None,
            "ai_cost_eur": quota.spent_eur if quota else 0.0,
            "ai_limit_eur": quota.limit_eur,
            "tokens_in_month": tokens.get("tokens_in", 0),
            "tokens_out_month": tokens.get("tokens_out", 0),
            "needs_upgrade_notice": quota.needs_upgrade_notice if hasattr(quota, "needs_upgrade_notice") else None,
            "metrics_last_flushed": metrics.get_last_flush_ts() if hasattr(metrics, "get_last_flush_ts") else None,
        },
    }
