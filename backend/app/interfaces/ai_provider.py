from abc import ABC, abstractmethod

class AiProvider(ABC):
    @abstractmethod
    async def extract_fields(self, text: str) -> dict:
        pass

    @abstractmethod
    async def generate_summary(self, lead_data: dict) -> str:
        pass

    @abstractmethod
    async def generate_reply(self, message: str, context: dict) -> str:
        pass
