"""Add quota fields and normalize tenant plans."""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = "0014_quota_fields_and_plan_enum"
down_revision = "0013_add_roles_enum_super_admin"
branch_labels = None
depends_on = None


plan_enum = sa.Enum("BASE", "PRO", "ELITE", name="plan_enum")
ia_plan_enum = sa.Enum("BASE", "PRO", "ELITE", name="ia_plan_enum")
usage_mode_enum = sa.Enum("ACTIVE", "SAVING", "LOCKED", name="usage_mode")


def upgrade():
    conn = op.get_bind()
    plan_enum.create(conn, checkfirst=True)
    ia_plan_enum.create(conn, checkfirst=True)
    usage_mode_enum.create(conn, checkfirst=True)

    # Normalizar valores existentes a mayúsculas antes de forzar Enum
    op.execute("UPDATE tenants SET plan = UPPER(plan) WHERE plan IS NOT NULL")
    op.execute("UPDATE tenants SET ia_plan = UPPER(ia_plan) WHERE ia_plan IS NOT NULL")

    op.alter_column(
        "tenants",
        "plan",
        existing_type=sa.String(length=50),
        type_=plan_enum,
        existing_nullable=False,
        server_default="BASE",
    )
    op.alter_column(
        "tenants",
        "ia_plan",
        existing_type=sa.String(length=10),
        type_=ia_plan_enum,
        existing_nullable=False,
        server_default="BASE",
    )

    op.add_column(
        "tenants",
        sa.Column(
            "usage_mode",
            usage_mode_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "usage_monthly",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "usage_limit_monthly",
            sa.Float(),
            nullable=True,
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "usage_reset_day",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "needs_upgrade_notice",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_table(
        "conversation_templates",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "schema_json",
            pg.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_conversation_templates_tenant_is_default",
        "conversation_templates",
        ["tenant_id", "is_default"],
    )

    op.add_column(
        "tenants",
        sa.Column(
            "default_template_id",
            pg.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_tenants_default_template",
        "tenants",
        "conversation_templates",
        ["default_template_id"],
        ["id"],
        ondelete="SET NULL",
    )

    templates_table = sa.table(
        "conversation_templates",
        sa.column("id", pg.UUID(as_uuid=True)),
        sa.column("tenant_id", pg.UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("schema_json", pg.JSONB),
        sa.column("is_default", sa.Boolean),
    )
    op.bulk_insert(
        templates_table,
        [
            {
                "id": uuid4(),
                "tenant_id": None,
                "name": "Lead simple",
                "description": "Captura contacto básico con IA opcional.",
                "schema_json": {
                    "blocks": [
                        {"id": "welcome", "type": "message", "text": "Hola, ¿en qué podemos ayudarte?"},
                        {
                            "id": "contact",
                            "type": "input",
                            "text": "Déjame tu email para enviarte opciones.",
                            "save_as": "email",
                            "next": "thanks",
                        },
                        {"id": "thanks", "type": "message", "text": "¡Gracias! Te contactamos en breve."},
                    ]
                },
                "is_default": True,
            },
            {
                "id": uuid4(),
                "tenant_id": None,
                "name": "Demo cita",
                "description": "Flujo con propuesta de cita rápida.",
                "schema_json": {
                    "blocks": [
                        {"id": "welcome", "type": "message", "text": "Te ayudamos a reservar una cita."},
                        {
                            "id": "ask_slot",
                            "type": "appointment",
                            "text": "Elige día y hora.",
                            "next": "summary",
                        },
                        {"id": "summary", "type": "message", "text": "Reserva registrada. Te confirmamos pronto."},
                    ]
                },
                "is_default": False,
            },
        ],
    )


def downgrade():
    op.drop_index(
        "ix_conversation_templates_tenant_is_default",
        table_name="conversation_templates",
    )
    op.drop_constraint("fk_tenants_default_template", "tenants", type_="foreignkey")
    op.drop_column("tenants", "default_template_id")
    op.drop_table("conversation_templates")
    op.drop_column("tenants", "needs_upgrade_notice")
    op.drop_column("tenants", "usage_reset_day")
    op.drop_column("tenants", "usage_limit_monthly")
    op.drop_column("tenants", "usage_monthly")
    op.drop_column("tenants", "usage_mode")

    op.alter_column(
        "tenants",
        "ia_plan",
        existing_type=ia_plan_enum,
        type_=sa.String(length=10),
        existing_nullable=False,
        server_default="BASE",
        postgresql_using="ia_plan::text",
    )
    op.alter_column(
        "tenants",
        "plan",
        existing_type=plan_enum,
        type_=sa.String(length=50),
        existing_nullable=False,
        server_default="BASE",
        postgresql_using="plan::text",
    )

    conn = op.get_bind()
    usage_mode_enum.drop(conn, checkfirst=True)
    ia_plan_enum.drop(conn, checkfirst=True)
    plan_enum.drop(conn, checkfirst=True)
