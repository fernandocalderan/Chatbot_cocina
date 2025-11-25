import pytest
from app.services.ai.openai_service import OpenAIService

@pytest.mark.asyncio
async def test_extract_fields_returns_dict(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    service = OpenAIService()

    class FakeResp:
        class Choices:
            content = '{"metros":10,"estilo":"moderno","presupuesto":"10k","urgencia":"alta"}'
            message = type("x", (), {"content": content})
        choices = [Choices]

    monkeypatch.setattr(service.client.chat.completions, "create", lambda **k: FakeResp())

    result = await service.extract_fields("Quiero una cocina moderna de 10 metros")
    assert result["metros"] == 10
