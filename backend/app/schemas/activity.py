from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class ActivitySchema(BaseModel):
    id: Optional[str] = None
    tenant_id: Optional[str] = None
    lead_id: Optional[str] = None
    user_id: Optional[str] = None
    type: Literal["nota", "llamada", "email", "whatsapp", "reunión", "cambio_estado"]
    content: str
    meta: Optional[dict] = None
    created_at: Optional[datetime] = None
