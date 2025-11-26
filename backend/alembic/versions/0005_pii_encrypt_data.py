"""encrypt legacy pii data

Revision ID: 0005_pii_encrypt_data
Revises: 0004_pii_schema
Create Date: 2025-02-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.services.pii_service import PIIService

# revision identifiers, used by Alembic.
revision: str = "0005_pii_encrypt_data"
down_revision: Union[str, None] = "0004_pii_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    meta = sa.MetaData()
    leads = sa.Table(
        "leads",
        meta,
        sa.Column("id", pg.UUID(as_uuid=True)),
        sa.Column("tenant_id", pg.UUID(as_uuid=True)),
        sa.Column("metadata", pg.JSONB),
        sa.Column("pii_version", sa.SmallInteger),
    )
    messages = sa.Table(
        "messages",
        meta,
        sa.Column("id", sa.BigInteger),
        sa.Column("tenant_id", pg.UUID(as_uuid=True)),
        sa.Column("content", sa.Text),
        sa.Column("pii_version", sa.SmallInteger),
    )
    pii = PIIService()

    # Normalize legacy rows to version 0 to process
    bind.execute(
        sa.text(
            "UPDATE leads SET pii_version=0 WHERE pii_version IS NULL OR pii_version=1"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE messages SET pii_version=0 WHERE pii_version IS NULL OR pii_version=1"
        )
    )

    # Encrypt leads in small batches
    while True:
        rows = bind.execute(
            sa.select(leads.c.id, leads.c.tenant_id, leads.c.metadata)
            .where(leads.c.pii_version == 0)
            .limit(200)
        ).fetchall()
        if not rows:
            break
        for row in rows:
            meta_val = row.metadata or {}
            new_meta, changed = pii.encrypt_meta(meta_val, str(row.tenant_id))
            if changed:
                bind.execute(
                    leads.update()
                    .where(leads.c.id == row.id)
                    .values(metadata=new_meta, pii_version=1)
                )
            else:
                bind.execute(
                    leads.update().where(leads.c.id == row.id).values(pii_version=1)
                )

    # Encrypt messages containing PII
    while True:
        rows = bind.execute(
            sa.select(messages.c.id, messages.c.tenant_id, messages.c.content)
            .where(messages.c.pii_version == 0)
            .limit(200)
        ).fetchall()
        if not rows:
            break
        for row in rows:
            content = row.content or ""
            encrypted, changed = pii.encrypt_message_content(
                content, str(row.tenant_id)
            )
            if changed:
                bind.execute(
                    messages.update()
                    .where(messages.c.id == row.id)
                    .values(content=encrypted, pii_version=1)
                )
            else:
                bind.execute(
                    messages.update()
                    .where(messages.c.id == row.id)
                    .values(pii_version=1)
                )


def downgrade() -> None:
    # No-op: data remains encrypted
    pass
