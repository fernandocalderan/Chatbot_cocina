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


class UsageMode(str, Enum):
    ACTIVE = "ACTIVE"
    SAVING = "SAVING"
    LOCKED = "LOCKED"


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_code = sa.Column(sa.String(20), nullable=False, unique=True, index=True)
    name = sa.Column(sa.String(255), nullable=False, index=True)
    contact_email = sa.Column(sa.String(320), nullable=True)
    plan = sa.Column(
        sa.Enum(PlanEnum, name="plan_enum"), nullable=False, server_default=PlanEnum.BASE.value
    )
    ia_enabled = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    use_ia = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    ia_plan = sa.Column(
        sa.Enum(PlanEnum, name="ia_plan_enum"), nullable=False, server_default=PlanEnum.BASE.value
    )
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
    vertical_key = sa.Column(sa.String(64), nullable=True)
    # Consolidación de flows:
    # - flow_mode = 'LEGACY' (compat) o 'VERTICAL' (usa flow publicado + vertical templates)
    # - active_flow_id apunta al FlowVersioned activo (si aplica)
    flow_mode = sa.Column(sa.String(32), nullable=False, server_default="LEGACY")
    active_flow_id = sa.Column(pg.UUID(as_uuid=True), nullable=True)
    usage_mode = sa.Column(
        sa.Enum(UsageMode, name="usage_mode"), nullable=False, server_default=UsageMode.ACTIVE.value
    )
    usage_monthly = sa.Column(sa.Float, nullable=False, server_default="0")
    usage_limit_monthly = sa.Column(sa.Float, nullable=True)
    usage_reset_day = sa.Column(sa.Integer, nullable=False, server_default="1")
    needs_upgrade_notice = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    default_template_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("conversation_templates.id"), nullable=True)
    default_template = sa.orm.relationship(
        "ConversationTemplate",
        foreign_keys=[default_template_id],
        lazy="joined",
    )
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
