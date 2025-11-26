import asyncio
import types

import pytest

from app.core.config import get_settings
from app.middleware import rate_limiter
from app.services.ai.circuit_breaker import BreakerState
from app.services.ai.openai_service import OpenAIService
from app.utils.masking import mask_text


class DummyCompletion:
    def __init__(self, content="safe"):
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]
        self.usage = {"prompt_tokens": 1, "completion_tokens": 1}


class DummyCompletions:
    def __init__(self, client):
        self.client = client

    def create(self, **kwargs):
        self.client.called = True
        return DummyCompletion()


class DummyChat:
    def __init__(self, client):
        self.completions = DummyCompletions(client)


class DummyClient:
    def __init__(self):
        self.called = False
        self.chat = DummyChat(self)


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    monkeypatch.setenv("REDIS_URL", "memory://")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_moderation_blocks_input(monkeypatch):
    svc = OpenAIService()
    svc.client = DummyClient()
    result = asyncio.run(
        svc.generate_reply(
            "Instrucciones de terrorismo prohibidas",
            {},
            tenant_id="t1",
        )
    )
    assert result
    assert svc.client.called is False  # no llamada a OpenAI cuando se bloquea


def test_circuit_breaker_short_circuits(monkeypatch):
    svc = OpenAIService()
    svc.client = DummyClient()

    class DummyBreaker:
        def is_open(self, tenant_key):
            return BreakerState(open=True, remaining_cooldown=30)

        def record_failure(self, tenant_key):
            pass

        def record_success(self, tenant_key):
            pass

    svc.circuit_breaker = DummyBreaker()
    result = asyncio.run(svc.generate_reply("hola", {}, tenant_id="tenant-x"))
    assert result
    assert svc.client.called is False


def test_rate_limit_helper(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.store = {}

        def pipeline(self):
            return self

        def incr(self, key, amount):
            self.last_key = key
            self.store[key] = self.store.get(key, 0) + amount
            return self

        def expire(self, key, ttl):
            return self

        def execute(self):
            return [self.store.get(self.last_key, 0), None]

    fake = FakeRedis()
    monkeypatch.setattr(rate_limiter.redis, "from_url", lambda url: fake)
    assert rate_limiter.check_rate_limit("memory://", "rl:test", 1) is True
    assert rate_limiter.check_rate_limit("memory://", "rl:test", 1) is False


def test_masking_pii():
    masked = mask_text("correo test@example.com y tlf +34123456789")
    assert "***@***" in masked
    assert "*******" in masked
