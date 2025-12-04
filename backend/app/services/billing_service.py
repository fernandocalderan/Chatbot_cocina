from typing import Optional

import stripe

from app.core.config import get_settings
from app.models.tenants import PlanEnum

settings = get_settings()
stripe.api_key = settings.stripe_api_key


def map_price_to_plan(price_id: str) -> Optional[PlanEnum]:
    if price_id == settings.stripe_price_base:
        return PlanEnum.BASE
    if price_id == settings.stripe_price_pro:
        return PlanEnum.PRO
    if price_id == settings.stripe_price_elite:
        return PlanEnum.ELITE
    return None


def create_checkout_session(tenant_id: str, price_id: str) -> str:
    base_url = settings.panel_url or "http://localhost:8501"
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_creation="if_required",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{base_url}/billing/success?tenant_id={tenant_id}",
        cancel_url=f"{base_url}/billing/cancel?tenant_id={tenant_id}",
        metadata={"tenant_id": tenant_id},
    )
    return session.url
