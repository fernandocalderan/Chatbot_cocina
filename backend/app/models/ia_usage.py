"""
Modelo IAUsage
==============

Tabla de auditoría de consumo de IA por tenant. Esta tabla será usada para:

- Agregados diarios / mensuales de tokens y coste.
- Enforcamiento de límites de plan (Base/Pro/Elite).
- Exposición de métricas en endpoints de observabilidad/panel.

La lógica de negocio (servicio de cuotas y wiring en openai) se añadirá
en pasos posteriores para mantener un orden de construcción limpio.
"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.db.base import Base


class IAUsage(Base):
    __tablename__ = "ia_usage"

    # Identificador único de la entrada de consumo
    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant al que se le imputa el consumo
    tenant_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Fecha lógica del consumo (no necesariamente created_at)
    date = sa.Column(sa.Date(), nullable=False, server_default=sa.func.current_date())

    # Modelo concreto de IA utilizado (gpt-4.1, gpt-4.1-mini, etc.)
    model = sa.Column(sa.String(100), nullable=False)

    # Tokens de entrada (prompt)
    tokens_in = sa.Column(sa.Integer(), nullable=False, server_default="0")

    # Tokens de salida (completion)
    tokens_out = sa.Column(sa.Integer(), nullable=False, server_default="0")

    # Coste imputado en EUR (aprox, según pricing table de modelos)
    # precision=12, scale=6 -> hasta 999.999,999999 €
    cost_eur = sa.Column(
        sa.Numeric(precision=12, scale=6), nullable=False, server_default="0"
    )

    # Timestamp de creación del registro
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )

    # Relación con el tenant (opcional, para navegación ORM)
    tenant = relationship("Tenant", back_populates="ia_usages", lazy="joined")


# Índice compuesto eficiente para queries por tenant+date
sa.Index(
    "ix_ia_usage_tenant_date",
    IAUsage.tenant_id,
    IAUsage.date,
)
