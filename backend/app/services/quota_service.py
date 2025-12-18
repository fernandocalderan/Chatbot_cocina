from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.models.tenants import BillingStatus, Tenant, UsageMode
from app.services.ia_usage_service import IAUsageService
from app.services.pricing import get_plan_limits


@dataclass
class QuotaStatus:
    mode: UsageMode
    spent_eur: float
    limit_eur: Optional[float]
    remaining_eur: Optional[float]
    reason: Optional[str] = None
    billing_status: Optional[BillingStatus] = None
    needs_upgrade_notice: bool = False

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value if isinstance(self.mode, UsageMode) else self.mode,
            "spent_eur": self.spent_eur,
            "limit_eur": self.limit_eur,
            "remaining_eur": self.remaining_eur,
            "reason": self.reason,
            "billing_status": self.billing_status.value if isinstance(self.billing_status, BillingStatus) else self.billing_status,
            "needs_upgrade_notice": self.needs_upgrade_notice,
        }


class QuotaService:
    SOFT_THRESHOLD = 0.8  # 80% → modo ahorro
    LOCKED_MESSAGE = "Has alcanzado el límite de IA de tu plan. Puedes seguir con respuestas básicas o actualizar tu plan."
    CTA_UPGRADE = {"label": "Mejorar plan", "action": "upgrade"}

    @staticmethod
    def evaluate(db: Session, tenant: Tenant) -> QuotaStatus:
        """
        Calcula el modo de uso del tenant (ACTIVE/SAVING/LOCKED) según consumo y estado de billing.
        Persiste un snapshot ligero en la tabla tenants para que UI/panel puedan leerlo rápido.
        """
        if tenant is None or db is None:
            return QuotaStatus(
                mode=UsageMode.LOCKED,
                spent_eur=0.0,
                limit_eur=0.0,
                remaining_eur=0.0,
                reason="tenant_not_found",
            )

        billing_status = getattr(tenant, "billing_status", BillingStatus.ACTIVE)
        limits = get_plan_limits(getattr(tenant, "plan", None))
        plan_limit = limits.get("max_ia_cost")
        limit_eur = IAUsageService._resolve_limit_eur(tenant)
        spent = IAUsageService.monthly_cost(db, tenant.id)

        mode = UsageMode.ACTIVE
        reason = None

        if billing_status and billing_status != BillingStatus.ACTIVE:
            mode = UsageMode.LOCKED
            reason = "billing_inactive"
        elif plan_limit == 0 or getattr(tenant, "ia_enabled", None) is False or getattr(tenant, "use_ia", None) is False:
            # Plan sin IA o deshabilitado explícitamente → seguir operando sin IA pero señalizar upgrade
            mode = UsageMode.SAVING
            reason = "ia_disabled"
        elif limit_eur != float("inf") and float(limit_eur) <= 0:
            # Límite explícito 0 → tratar como IA deshabilitada (no bloquear el tenant)
            mode = UsageMode.SAVING
            reason = "ia_disabled_limit"
        else:
            if limit_eur != float("inf"):
                if spent >= limit_eur:
                    mode = UsageMode.LOCKED
                    reason = "quota_exceeded"
                elif spent >= limit_eur * QuotaService.SOFT_THRESHOLD:
                    mode = UsageMode.SAVING

        remaining = None if limit_eur == float("inf") else max(limit_eur - spent, 0.0)
        QuotaService._persist_snapshot(db, tenant, mode, spent, None if limit_eur == float("inf") else limit_eur, reason)
        return QuotaStatus(
            mode=mode,
            spent_eur=float(spent or 0.0),
            limit_eur=None if limit_eur == float("inf") else float(limit_eur),
            remaining_eur=remaining if remaining is None else float(remaining),
            reason=reason,
            billing_status=billing_status,
            needs_upgrade_notice=mode != UsageMode.ACTIVE or bool(reason),
        )

    @staticmethod
    def enforce(db: Session, tenant: Tenant) -> QuotaStatus:
        """
        Lanza HTTP 402 si el tenant está en modo LOCKED, incluyendo payload para UI de upgrade.
        """
        status_snapshot = QuotaService.evaluate(db, tenant)
        if status_snapshot.mode == UsageMode.LOCKED:
            logger.warning(
                {
                    "event": "tenant_locked_by_quota",
                    "tenant_id": str(getattr(tenant, "id", "")),
                    "reason": status_snapshot.reason,
                    "spent": status_snapshot.spent_eur,
                    "limit": status_snapshot.limit_eur,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "code": "upgrade_required",
                    "message": QuotaService.LOCKED_MESSAGE,
                    "cta": QuotaService.CTA_UPGRADE,
                    "quota_status": status_snapshot.to_dict(),
                    "needs_upgrade_notice": True,
                },
            )
        return status_snapshot

    @staticmethod
    def _persist_snapshot(
        db: Session,
        tenant: Tenant,
        mode: UsageMode,
        spent: float,
        limit: Optional[float],
        reason: Optional[str],
    ) -> None:
        """Guarda campos rápidos en tenants para que el panel/widget puedan leerlos sin cálculos."""
        try:
            tenant.usage_mode = mode
            tenant.usage_monthly = float(spent or 0.0)
            tenant.usage_limit_monthly = limit
            tenant.needs_upgrade_notice = mode != UsageMode.ACTIVE or bool(reason)
            db.add(tenant)
            db.commit()
        except Exception:
            db.rollback()
            # No bloquear la request por errores de persistencia
