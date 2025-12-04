import uuid
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class BillingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"
    INCOMPLETE = "INCOMPLETE"


class PlanEnum(str, Enum):
    BASE = "BASE"
    PRO = "PRO"
    ELITE = "ELITE"


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String(255), nullable=False, index=True)
    contact_email = sa.Column(sa.String(320), nullable=True)
    plan = sa.Column(sa.String(50), nullable=False, server_default="Base")
    use_ia = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    ia_plan = sa.Column(sa.String(10), nullable=False, server_default="base")
    ia_monthly_limit_eur = sa.Column(sa.Numeric(precision=12, scale=2), nullable=True)
    billing_status = sa.Column(
        sa.Enum(BillingStatus, name="billing_status"), nullable=True, server_default=BillingStatus.ACTIVE.value
    )
    stripe_customer_id = sa.Column(sa.String(255), nullable=True)
    stripe_subscription_id = sa.Column(sa.String(255), nullable=True)
    flags_ia = sa.Column(
        pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")
    )
    branding = sa.Column(
        pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")
    )
    workdays = sa.Column(pg.ARRAY(sa.Integer), nullable=True)
    opening_hours = sa.Column(pg.JSONB, nullable=True)
    slot_duration = sa.Column(sa.Integer, nullable=True)
    idioma_default = sa.Column(sa.String(10), nullable=False, server_default="es")
    timezone = sa.Column(sa.String(64), nullable=False, server_default="Europe/Madrid")
    google_calendar_connected = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.text("false")
    )
    google_refresh_token = sa.Column(sa.String(1024), nullable=True)
    google_calendar_id = sa.Column(sa.String(255), nullable=True)
    microsoft_calendar_connected = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.text("false")
    )
    microsoft_refresh_token = sa.Column(sa.String(1024), nullable=True)
    microsoft_calendar_id = sa.Column(sa.String(255), nullable=True)
    ai_cost = sa.Column(sa.Float, nullable=False, server_default="0")
    ai_monthly_limit = sa.Column(sa.Float, nullable=False, server_default="100")
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
    ia_usages = sa.orm.relationship(
        "IAUsage",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
