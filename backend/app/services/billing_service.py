from typing import Optional

import stripe

from app.core.config import get_settings
from app.models.tenants import PlanEnum

settings = get_settings()
stripe.api_key = settings.stripe_api_key


def _ensure_api_key():
    if not stripe.api_key:
        raise RuntimeError("stripe_api_key_not_configured")


def map_price_to_plan(price_id: str) -> Optional[PlanEnum]:
    if price_id == settings.stripe_price_base:
        return PlanEnum.BASE
    if price_id == settings.stripe_price_pro:
        return PlanEnum.PRO
    if price_id == settings.stripe_price_elite:
        return PlanEnum.ELITE
    return None


def create_checkout_session(tenant_id: str, price_id: str) -> str:
    _ensure_api_key()
    base_url = settings.panel_url or "http://localhost:8501"
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_creation="if_required",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{base_url}/billing/success?tenant_id={tenant_id}",
        cancel_url=f"{base_url}/billing/cancel?tenant_id={tenant_id}",
        metadata={"tenant_id": tenant_id, "price_id": price_id},
    )
    return session.url


def create_billing_portal_session(customer_id: str) -> Optional[str]:
    """
    Devuelve URL del Customer Portal de Stripe para gestionar la suscripción.
    """
    _ensure_api_key()
    if not customer_id:
        return None
    base_url = settings.panel_url or "http://localhost:8501"
    portal = stripe.billing_portal.Session.create(
        customer=customer_id, return_url=f"{base_url}/"
    )
    return portal.url


def subscription_overview(subscription_id: str) -> dict:
    """
    Obtiene info resumida de una suscripción desde Stripe.
    """
    _ensure_api_key()
    if not subscription_id:
        return {}
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
    except Exception:
        return {}
    renew_ts = sub.get("current_period_end")
    price_id = None
    try:
        items = sub.get("items", {}).get("data") or []
        if items:
            price_id = items[0].get("price", {}).get("id")
    except Exception:
        price_id = None
    return {
        "stripe_status": sub.get("status"),
        "current_period_end": renew_ts,
        "price_id": price_id,
    }
