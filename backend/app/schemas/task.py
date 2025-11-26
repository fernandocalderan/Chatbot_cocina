from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class TaskSchema(BaseModel):
    id: Optional[str] = None
    tenant_id: Optional[str] = None
    lead_id: Optional[str] = None
    owner_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: Literal["pendiente", "en_progreso", "hecha", "cancelada"] = "pendiente"
    due_date: Optional[datetime] = None
    priority: Literal["baja", "media", "alta"] = "media"
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
