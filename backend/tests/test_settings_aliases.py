from app.core.config import get_settings


def test_admin_api_key_alias(monkeypatch):
    monkeypatch.delenv("ADMIN_API_TOKEN", raising=False)
    monkeypatch.setenv("ADMIN_API_KEY", "alias-key")
    get_settings.cache_clear()
    assert get_settings().admin_api_token == "alias-key"
    get_settings.cache_clear()

