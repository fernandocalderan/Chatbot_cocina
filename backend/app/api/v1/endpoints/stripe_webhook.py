import stripe
from fastapi import APIRouter, HTTPException, Request

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.tenants import BillingStatus, Tenant
from app.services.billing_service import map_price_to_plan

router = APIRouter(prefix="/stripe", tags=["billing"])
settings = get_settings()

# 🔥 INICIALIZAR STRIPE (faltaba en tu código)
stripe.api_key = settings.stripe_api_key


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # 🔥 SI EL SECRET ES INCORRECTO → 400
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 🔥 Conexión DB
    session = SessionLocal()

    # ----------- MANEJO DE SUBSCRIPCIONES -----------
    if event["type"] in (
        "customer.subscription.created",
        "customer.subscription.updated",
    ):
        sub = event["data"]["object"]
        tenant_id = sub.get("metadata", {}).get("tenant_id")
        tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()

        if tenant:
            price_id = sub["items"]["data"][0]["price"]["id"]
            plan = map_price_to_plan(price_id)

            if plan:
                tenant.plan = plan.value if hasattr(plan, "value") else plan

            tenant.stripe_subscription_id = sub.get("id")
            tenant.billing_status = BillingStatus.ACTIVE
            session.commit()

    if event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        tenant_id = sub.get("metadata", {}).get("tenant_id")
        tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()

        if tenant:
            tenant.billing_status = BillingStatus.CANCELED
            session.commit()

    if event["type"] == "invoice.payment_failed":
        sub_id = event["data"]["object"].get("subscription")
        tenant = (
            session.query(Tenant)
            .filter(Tenant.stripe_subscription_id == sub_id)
            .first()
        )
        if tenant:
            tenant.billing_status = BillingStatus.PAST_DUE
            session.commit()

    if event["type"] == "invoice.paid":
        sub_id = event["data"]["object"].get("subscription")
        tenant = (
            session.query(Tenant)
            .filter(Tenant.stripe_subscription_id == sub_id)
            .first()
        )
        if tenant:
            tenant.billing_status = BillingStatus.ACTIVE
            session.commit()

    return {"status": "ok"}
