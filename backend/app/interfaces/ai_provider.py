from abc import ABC, abstractmethod
from typing import Any, Optional


class AiProvider(ABC):
    @abstractmethod
    async def extract_fields(
        self, text: str, purpose: str = "extraction", tenant: Any = None, tenant_id: Optional[str] = None, language=None
    ) -> dict:
        pass

    @abstractmethod
    async def generate_summary(self, lead_data: dict, tenant: Any = None, tenant_id: Optional[str] = None, language=None) -> str:
        pass

    @abstractmethod
    async def generate_reply(
        self, message: str, context: dict, purpose: str = "reply_contextual", tenant: Any = None, tenant_id: Optional[str] = None, language=None
    ) -> str:
        pass
