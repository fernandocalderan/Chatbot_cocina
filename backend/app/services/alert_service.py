"""
AlertService
============

Servicio centralizado de alertas IA.
Envía notificaciones cuando un tenant:
  - Se acerca al límite IA (soft).
  - Supera el límite IA (hard).
  - Intenta usar IA después del límite.

Usa Slack (webhook) + Email (stub).
"""

import logging
import os

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AlertService:
    @staticmethod
    def send_slack_message(text: str) -> None:
        settings = get_settings()
        url = os.environ.get("SLACK_WEBHOOK_URL") or getattr(
            settings, "slack_webhook_url", None
        )
        if not url:
            logger.warning("[AlertService] Slack webhook no configurado.")
            return
        try:
            requests.post(url, json={"text": text}, timeout=5)
        except Exception as exc:
            logger.error(f"[AlertService] Error enviando Slack: {exc}")

    @staticmethod
    def send_email(to: str, subject: str, body: str) -> None:
        """
        Placeholder: sistema de email minimal.
        En producción, integrar SES, SendGrid o Mailgun.
        """
        try:
            logger.info(f"[EMAIL] To={to} | Subject={subject}\n{body}")
        except Exception:
            logger.error("[AlertService] Error simulando envío de email")

    # -------------------------------
    #      EVENTOS DE ALERTA IA
    # -------------------------------

    @staticmethod
    def notify_soft_limit(tenant, spent: float, limit: float):
        pct = (spent / limit) * 100 if limit else 0
        msg = (
            f":warning: *Soft Limit IA alcanzado*\n"
            f"Tenant: `{getattr(tenant, 'id', 'unknown')}` ({getattr(tenant, 'name', '')})\n"
            f"Consumo: {spent:.4f} € / {limit:.4f} € ({pct:.2f}%)"
        )
        AlertService.send_slack_message(msg)

    @staticmethod
    def notify_hard_limit(tenant, spent: float, limit: float):
        msg = (
            f":rotating_light: *HARD LIMIT IA EXCEDIDO*\n"
            f"Tenant: `{getattr(tenant, 'id', 'unknown')}` ({getattr(tenant, 'name', '')})\n"
            f"Consumo: {spent:.4f} € / {limit:.4f} €"
        )
        AlertService.send_slack_message(msg)

        admin_email = os.environ.get("ALERT_EMAIL_SUPERADMIN") or "admin@example.com"
        AlertService.send_email(
            to=admin_email,
            subject="OVER IA LIMIT ALERT",
            body=msg,
        )

        if hasattr(tenant, "contact_email") and tenant.contact_email:
            AlertService.send_email(
                to=tenant.contact_email,
                subject="[IMPORTANT] IA Limit reached",
                body=msg,
            )

    @staticmethod
    def notify_post_limit_use(tenant, spent: float, limit: float):
        msg = (
            f":no_entry_sign: *Intento de uso IA tras Hard Limit*\n"
            f"Tenant `{getattr(tenant, 'id', 'unknown')}` uso prohibido.\n"
            f"Spent={spent:.4f}, Limit={limit:.4f}"
        )
        AlertService.send_slack_message(msg)
