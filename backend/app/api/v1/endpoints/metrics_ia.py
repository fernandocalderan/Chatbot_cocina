from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.middleware.authz import require_any_role
from app.api.deps import get_tenant_id
from app.services.ia_usage_service import IAUsageService
from app.models.ia_usage import IAUsage

router = APIRouter(prefix="/metrics", tags=["metrics", "ia"])


def _serialize_usage_row(row: IAUsage) -> Dict[str, Any]:
    """Normaliza un registro IAUsage a un dict serializable."""
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "date": row.date.isoformat() if row.date else None,
        "model": row.model,
        "tokens_in": row.tokens_in,
        "tokens_out": row.tokens_out,
        "cost_eur": float(row.cost_eur or 0),
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get(
    "/ia/tenant/{tenant_id}",
    summary="IA usage metrics for a given tenant",
)
def get_ia_metrics_for_tenant(
    tenant_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: Any = Depends(require_any_role("OWNER", "ADMIN")),
) -> Dict[str, Any]:
    """
    Devuelve métricas de consumo de IA para un tenant concreto:

    - coste mensual total (EUR)
    - tokens de entrada/salida del mes
    - últimos N registros IAUsage (orden desc por created_at)
    """

    if limit <= 0:
        limit = 1
    if limit > 500:
        limit = 500

    total_cost = IAUsageService.monthly_cost(db, tenant_id)
    token_stats = IAUsageService.monthly_token_count(db, tenant_id)
    latest_rows: List[IAUsage] = IAUsageService.latest_usage(db, tenant_id, limit=limit)

    return {
        "tenant_id": tenant_id,
        "period": "current_month",
        "monthly": {
            "total_cost_eur": float(total_cost),
            "tokens_in": token_stats["tokens_in"],
            "tokens_out": token_stats["tokens_out"],
        },
        "latest": [_serialize_usage_row(row) for row in latest_rows],
    }


@router.get(
    "/ia/self",
    summary="IA usage metrics for current tenant (admin scope)",
)
def get_ia_metrics_self(
    limit: int = 50,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: Any = Depends(require_any_role("OWNER", "ADMIN")),
) -> Dict[str, Any]:
    """
    Métricas de IA para el tenant del usuario autenticado (rol admin/owner).
    """
    if limit <= 0:
        limit = 1
    if limit > 500:
        limit = 500

    total_cost = IAUsageService.monthly_cost(db, tenant_id)
    token_stats = IAUsageService.monthly_token_count(db, tenant_id)
    latest_rows: List[IAUsage] = IAUsageService.latest_usage(db, tenant_id, limit=limit)

    return {
        "tenant_id": tenant_id,
        "period": "current_month",
        "monthly": {
            "total_cost_eur": float(total_cost),
            "tokens_in": token_stats["tokens_in"],
            "tokens_out": token_stats["tokens_out"],
        },
        "latest": [_serialize_usage_row(row) for row in latest_rows],
    }
