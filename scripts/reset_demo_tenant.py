#!/usr/bin/env python3
"""
Seed/Reset de Tenant Demo para demos comerciales.

- Crea/actualiza un tenant demo con datos de leads, citas y consumo IA.
- No toca otros tenants.
"""
import os
import sys
import uuid
import datetime as dt
from decimal import Decimal
import json

from sqlalchemy import create_engine, text


DEMO_TENANT_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DEMO_NAME = "Studio Demo Cocinas"
DEMO_LOGO_URL = "https://dummyimage.com/160x60/6b5b95/ffffff&text=Studio+Demo"
DEMO_ALLOWED_ORIGINS = ["https://demo.opunnence.com"]


def get_session():
    url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/chatbot")
    engine = create_engine(url)
    return engine


def reset_demo():
    engine = get_session()
    conn = engine.connect()
    try:
        # Limpia datos previos
        conn.execute(text("DELETE FROM ia_usage WHERE tenant_id=:id"), {"id": DEMO_TENANT_ID})
        conn.execute(text("DELETE FROM appointments WHERE tenant_id=:id"), {"id": DEMO_TENANT_ID})
        conn.execute(text("DELETE FROM leads WHERE tenant_id=:id"), {"id": DEMO_TENANT_ID})
        conn.execute(text("DELETE FROM tenants WHERE id=:id"), {"id": DEMO_TENANT_ID})
        conn.commit()

        branding = {
            "logo_url": DEMO_LOGO_URL,
            "theme": "violet",
            "primary_color": "#6B5B95",
            "allowed_widget_origins": DEMO_ALLOWED_ORIGINS,
        }

        conn.execute(
            text(
                """
                INSERT INTO tenants (
                    id, name, plan, ia_plan, ia_enabled, use_ia, billing_status,
                    ia_monthly_limit_eur, usage_mode, usage_monthly, usage_limit_monthly,
                    needs_upgrade_notice, idioma_default, timezone, branding
                ) VALUES (
                    :id, :name, 'PRO', 'PRO', true, true, 'ACTIVE',
                    :ia_limit, 'SAVING', :usage, :usage_limit,
                    true, 'es', 'Europe/Madrid', CAST(:branding_json AS jsonb)
                )
                """
            ),
            {
                "id": DEMO_TENANT_ID,
                "name": DEMO_NAME,
                "ia_limit": Decimal("25.00"),
                "usage": 21.0,
                "usage_limit": 25.0,
                "branding_json": json.dumps(branding),
            },
        )

        # Leads
        now = dt.datetime.now(dt.timezone.utc)
        lead_statuses = ["nuevo", "contactado", "cita", "contactado", "cita", "cerrado"]
        leads = []
        for i in range(18):
            status = lead_statuses[i % len(lead_statuses)]
            leads.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": DEMO_TENANT_ID,
                    "status": status,
                    "origen": "demo",
                    "idioma": "es",
                    "metadata_json": json.dumps({
                        "contact_name": f"Lead Demo {i+1}",
                        "contact_email": f"lead{i+1}@demo.com",
                        "project_type": "kitchen",
                    }),
                    "created_at": now - dt.timedelta(days=i // 2),
                }
            )
        conn.execute(
            text(
                """
                INSERT INTO leads (id, tenant_id, session_id, origen, status, score, score_breakdown_json, metadata, idioma, timezone, created_at)
                VALUES (:id, :tenant_id, NULL, :origen, :status, NULL, '{}'::jsonb, CAST(:metadata_json AS jsonb), :idioma, NULL, :created_at)
                """
            ),
            leads,
        )

        # Citas (6 confirmadas)
        appts = []
        for i in range(6):
            start = now + dt.timedelta(days=i + 1)
            appts.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": DEMO_TENANT_ID,
                    "lead_id": leads[i]["id"] if i < len(leads) else None,
                    "slot_start": start,
                    "slot_end": start + dt.timedelta(minutes=45),
                    "estado": "confirmed",
                    "origen": "demo",
                    "notas": "Demo booking",
                }
            )
        conn.execute(
            text(
                """
                INSERT INTO appointments (id, tenant_id, lead_id, slot_start, slot_end, estado, origen, notas)
                VALUES (:id, :tenant_id, :lead_id, :slot_start, :slot_end, :estado, :origen, :notas)
                """
            ),
            appts,
        )

        # IA Usage (~21€ usado)
        usage_rows = []
        for i in range(10):
            day = now.date() - dt.timedelta(days=i)
            cost = Decimal("2.10") if i < 9 else Decimal("2.0")
            usage_rows.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": DEMO_TENANT_ID,
                    "date": day,
                    "model": "gpt-4.1-mini",
                    "tokens_in": 12000 + i * 100,
                    "tokens_out": 8000 + i * 80,
                    "cost_eur": cost,
                    "session_id": f"demo-session-{i}",
                    "call_type": "chat",
                }
            )
        conn.execute(
            text(
                """
                INSERT INTO ia_usage (id, tenant_id, date, model, tokens_in, tokens_out, session_id, call_type, cost_eur)
                VALUES (:id, :tenant_id, :date, :model, :tokens_in, :tokens_out, :session_id, :call_type, :cost_eur)
                """
            ),
            usage_rows,
        )
        conn.commit()

        print("✅ Tenant demo reseteado con datos de ejemplo.")
    finally:
        conn.close()


if __name__ == "__main__":
    reset_demo()
