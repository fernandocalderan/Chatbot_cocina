"""Add quota fields and normalize tenant plans.

Revision ID: 0014_quota_fields_and_plan_enum
Revises: 0013_add_roles_enum_super_admin
Create Date: 2025-12-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0014_quota_fields_and_plan_enum"
down_revision = "0013_add_roles_enum_super_admin"
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Crear ENUM si no existe
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plan_enum') THEN
                CREATE TYPE plan_enum AS ENUM ('BASE', 'PRO', 'ELITE');
            END IF;
        END$$;
        """
    )

    # 2️⃣ Quitar DEFAULT para evitar error de casteo
    op.execute(
        """
        ALTER TABLE tenants
        ALTER COLUMN plan DROP DEFAULT;
        """
    )

    # 3️⃣ Normalizar valores existentes
    op.execute(
        """
        UPDATE tenants
        SET plan = UPPER(TRIM(plan))
        WHERE plan IS NOT NULL;
        """
    )

    # 4️⃣ Cambiar tipo a ENUM
    op.execute(
        """
        ALTER TABLE tenants
        ALTER COLUMN plan TYPE plan_enum
        USING plan::plan_enum;
        """
    )

    # 5️⃣ Restaurar DEFAULT correcto
    op.execute(
        """
        ALTER TABLE tenants
        ALTER COLUMN plan SET DEFAULT 'BASE';
        """
    )


def downgrade():
    # Volver a VARCHAR si hiciera falta
    op.execute(
        """
        ALTER TABLE tenants
        ALTER COLUMN plan DROP DEFAULT;
        """
    )

    op.execute(
        """
        ALTER TABLE tenants
        ALTER COLUMN plan TYPE VARCHAR(32);
        """
    )

    op.execute(
        """
        ALTER TABLE tenants
        ALTER COLUMN plan SET DEFAULT 'BASE';
        """
    )

    op.execute(
        """
        DROP TYPE IF EXISTS plan_enum;
        """
    )
