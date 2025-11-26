from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class LeadSchema(BaseModel):
    status: Literal["nuevo", "contactado", "en_propuesta", "negociación", "ganado", "perdido"] = "nuevo"
    owner_id: Optional[str] = None
    source: Optional[str] = None
    lost_reason: Optional[str] = None
    expected_value: Optional[Decimal] = None
    closed_at: Optional[datetime] = None
