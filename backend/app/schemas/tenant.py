from typing import Dict, List, Literal

from pydantic import BaseModel


class TenantSchema(BaseModel):
    use_ia: bool = False
    ia_plan: Literal["base", "pro", "elite"] = "base"
    workdays: List[int] | None = None
    opening_hours: Dict[str, str] | None = None
    slot_duration: int | None = None
    timezone: str | None = None
    google_calendar_connected: bool = False
    google_refresh_token: str | None = None
    google_calendar_id: str | None = None
    microsoft_calendar_connected: bool = False
    microsoft_refresh_token: str | None = None
    microsoft_calendar_id: str | None = None
