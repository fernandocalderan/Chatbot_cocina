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

    session = SessionLocal()
    try:
        event_type = event["type"]

        if event_type == "checkout.session.completed":
            checkout = event["data"]["object"]
            tenant_id = checkout.get("metadata", {}).get("tenant_id")
            price_id = checkout.get("metadata", {}).get("price_id")
            subscription_id = checkout.get("subscription")
            customer_id = checkout.get("customer")
            if not price_id and subscription_id:
                try:
                    sub = stripe.Subscription.retrieve(subscription_id)
                    items = sub.get("items", {}).get("data") or []
                    if items:
                        price_id = items[0].get("price", {}).get("id")
                except Exception:
                    price_id = None
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                plan = map_price_to_plan(price_id)
                if plan:
                    tenant.plan = plan.value if hasattr(plan, "value") else plan
                if subscription_id:
                    tenant.stripe_subscription_id = subscription_id
                if customer_id:
                    tenant.stripe_customer_id = customer_id
                tenant.billing_status = BillingStatus.ACTIVE
                session.commit()

        # ----------- MANEJO DE SUBSCRIPCIONES -----------
        if event_type in (
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

        if event_type == "customer.subscription.deleted":
            sub = event["data"]["object"]
            tenant_id = sub.get("metadata", {}).get("tenant_id")
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()

            if tenant:
                tenant.billing_status = BillingStatus.CANCELED
                session.commit()

        if event_type == "invoice.payment_failed":
            sub_id = event["data"]["object"].get("subscription")
            tenant = (
                session.query(Tenant)
                .filter(Tenant.stripe_subscription_id == sub_id)
                .first()
            )
            if tenant:
                tenant.billing_status = BillingStatus.PAST_DUE
                session.commit()

        if event_type == "invoice.paid":
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
    finally:
        session.close()
