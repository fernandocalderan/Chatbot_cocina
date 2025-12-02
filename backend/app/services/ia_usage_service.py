"""
IAUsageService
==============

Servicio dedicado a agregación y cálculo de uso de IA por tenant.

Responsabilidades:
- Registrar consumo (tokens + coste).
- Agregar por día, mes o rango.
- Calcular consumo total del periodo.
- Obtener coste total mensual.
- Preparar datos para métricas/panel.
"""

from datetime import date, datetime
from typing import List, Optional

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ia_usage import IAUsage
from app.models.tenants import Tenant


class IAQuotaExceeded(Exception):
    """Excepción lanzada cuando un tenant supera su cuota mensual de IA."""


PLAN_LIMITS = {
    "base": 10.0,
    "pro": 25.0,
    "elite": 100.0,
}

# Límites mensuales por plan en EUR (aprox, versión upper-case para compatibilidad)
PLAN_LIMITS_EUR: dict[str, float] = {
    "BASE": 10.0,
    "PRO": 25.0,
    "ELITE": 100.0,
}


class IAUsageService:
    @staticmethod
    def _plan_limit(tenant: Tenant) -> float:
        if tenant and getattr(tenant, "ai_monthly_limit", None) is not None:
            return float(tenant.ai_monthly_limit)
        plan = (getattr(tenant, "plan", None) or "base").lower()
        return PLAN_LIMITS.get(plan, PLAN_LIMITS["base"])

    @staticmethod
    def record_usage(
        db: Session,
        tenant_id: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost_eur: float,
        usage_date: date | None = None,
    ) -> Optional[IAUsage]:
        """Inserta un registro de consumo IA."""
        if db is None:
            return None
        usage = IAUsage(
            tenant_id=tenant_id,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_eur=cost_eur,
            date=usage_date or date.today(),
            created_at=datetime.utcnow(),
        )
        db.add(usage)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        return usage

    @staticmethod
    def monthly_usage(db: Session, tenant_id: str) -> List[IAUsage]:
        """Devuelve todos los registros del mes actual para un tenant."""
        if db is None:
            return []
        today = date.today()
        month_start = date(today.year, today.month, 1)
        return (
            db.query(IAUsage)
            .filter(
                IAUsage.tenant_id == tenant_id,
                IAUsage.date >= month_start,
            )
            .order_by(IAUsage.date.asc(), IAUsage.created_at.asc())
            .all()
        )

    @staticmethod
    def get_monthly_usage(db: Session, tenant_id: str) -> List[IAUsage]:
        # alias para compatibilidad previa
        return IAUsageService.monthly_usage(db, tenant_id)

    @staticmethod
    def monthly_cost(db: Session, tenant_id: str) -> float:
        """Retorna el coste total del mes."""
        if db is None:
            return 0.0
        today = date.today()
        month_start = date(today.year, today.month, 1)
        total = (
            db.query(func.sum(IAUsage.cost_eur))
            .filter(
                IAUsage.tenant_id == tenant_id,
                IAUsage.date >= month_start,
            )
            .scalar()
        )
        return float(total or 0)

    @staticmethod
    def total_monthly_cost(db: Session, tenant_id: str) -> float:
        # alias para compatibilidad previa
        return IAUsageService.monthly_cost(db, tenant_id)

    @staticmethod
    def monthly_token_count(db: Session, tenant_id: str) -> dict:
        """Agrupa tokens_in y tokens_out del mes actual."""
        if db is None:
            return {"tokens_in": 0, "tokens_out": 0}
        today = date.today()
        month_start = date(today.year, today.month, 1)

        result = (
            db.query(
                func.sum(IAUsage.tokens_in),
                func.sum(IAUsage.tokens_out),
            )
            .filter(
                IAUsage.tenant_id == tenant_id,
                IAUsage.date >= month_start,
            )
            .first()
        )

        tokens_in = int(result[0] or 0)
        tokens_out = int(result[1] or 0)

        return {"tokens_in": tokens_in, "tokens_out": tokens_out}

    @staticmethod
    def latest_usage(db: Session, tenant_id: str, limit: int = 20):
        """Devuelve los últimos N registros para panel/inspección."""
        if db is None:
            return []
        return (
            db.query(IAUsage)
            .filter(IAUsage.tenant_id == tenant_id)
            .order_by(IAUsage.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def enforce_limits(db: Session, tenant: Tenant):
        if tenant is None or db is None:
            return
        limit = IAUsageService._plan_limit(tenant)
        spent = IAUsageService.total_monthly_cost(db, str(tenant.id))
        if spent >= limit:
            raise IAQuotaExceeded("ia_monthly_quota_exceeded")
        if spent >= limit * 0.8:
            logger.warning(
                {
                    "event": "ia_quota_warning",
                    "tenant_id": str(tenant.id),
                    "spent": spent,
                    "limit": limit,
                }
            )

    # ========================
    #  Cálculo de costes IA
    # ========================

    @staticmethod
    def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
        """
        Estima el coste en EUR para una llamada, en función del modelo y los tokens.
        Precios aproximados; ajustar en producción según tarifas oficiales.
        """
        total_tokens = tokens_in + tokens_out
        price_per_million = {
            "gpt-4.1": 5.0,
            "gpt-4.1-mini": 1.5,
            "gpt-4.1-preview": 4.0,
        }
        normalized = (model or "").lower()
        if "gpt-4.1-mini" in normalized:
            key = "gpt-4.1-mini"
        elif "gpt-4.1-preview" in normalized:
            key = "gpt-4.1-preview"
        else:
            key = "gpt-4.1"
        per_million = price_per_million.get(key, 5.0)
        return float(per_million * (total_tokens / 1_000_000))

    # ========================
    #  Cuotas y enforcamiento
    # ========================

    @staticmethod
    def remaining_quota_eur(db: Session, tenant: Tenant) -> float:
        plan = (tenant.plan or "BASE").upper()
        limit = PLAN_LIMITS_EUR.get(plan, PLAN_LIMITS_EUR["BASE"])
        spent = IAUsageService.monthly_cost(db, tenant.id)
        return float(max(limit - spent, 0.0))

    @staticmethod
    def enforce_quota(
        db: Session,
        tenant: Tenant,
        estimated_cost_next_call: float = 0.0,
    ) -> None:
        """
        Verifica si el tenant puede realizar una nueva llamada IA.
        Lanza IAQuotaExceeded si el consumo proyectado supera el límite.
        """
        if tenant is None or db is None:
            return
        plan = (tenant.plan or "BASE").upper()
        limit = PLAN_LIMITS_EUR.get(plan, PLAN_LIMITS_EUR["BASE"])
        spent = IAUsageService.monthly_cost(db, tenant.id)
        projected = spent + estimated_cost_next_call
        if projected >= limit:
            raise IAQuotaExceeded(
                f"ia_monthly_quota_exceeded: tenant={tenant.id} plan={plan} spent={spent:.4f} limit={limit:.4f}"
            )
        if projected >= limit * 0.8:
            logger.warning(
                {
                    "event": "ia_quota_warning",
                    "tenant_id": str(tenant.id),
                    "spent": spent,
                    "limit": limit,
                    "projected": projected,
                }
            )
