import os
from pathlib import Path
import sys
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> str | None:
    # Evitar cargar dotenv durante tests (incluye fase de import/colección).
    if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST"):
        return None
    if os.getenv("DISABLE_DOTENV") == "1":
        return None
    backend_env = Path(__file__).resolve().parents[2] / ".env"
    if backend_env.exists():
        return str(backend_env)
    root_env = Path(__file__).resolve().parents[3] / ".env"
    if root_env.exists():
        return str(root_env)
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_resolve_env_file(),
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Cocinas Assistant API"
    environment: Literal["local", "staging", "production"] = "local"
    version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/chatbot"
    redis_url: str = "redis://redis:6379/0"
    log_level: str = "INFO"
    use_ia: bool = False
    ai_model: str = "gpt-4.1-mini"
    openai_api_key: str | None = None
    stripe_api_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_base: str | None = None
    stripe_price_pro: str | None = None
    stripe_price_elite: str | None = None
    panel_url: str | None = None
    maintenance_mode: bool = False
    maintenance_message: str = "Estamos en mantenimiento. Volvemos enseguida."
    panel_api_token: str | None = None
    storage_dir: str = "/tmp/chatbot_uploads"
    cors_origins: str | None = None  # comma-separated
    rate_limit_per_min: int = 120
    rate_limit_chat_per_ip: int = 60
    rate_limit_chat_per_tenant: int = 600
    rate_limit_widget_per_tenant: int = 20
    rate_limit_widget_per_ip: int = 60
    rate_limit_admin_per_min: int = 600
    rate_limit_admin_unauth_per_min: int = 30
    jwt_secret: str | None = None
    jwt_private_key_current: str | None = None
    jwt_private_key_previous: str | None = None
    jwt_key_current_id: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_exp_hours: int = 24
    ai_price_per_token_usd: float = 0.000002
    pii_key_current: str | None = None
    pii_key_previous: str | None = None
    ai_moderation_enabled: bool = True
    ai_moderation_strict_mode: bool = False
    ai_circuit_breaker_threshold: int = 5
    ai_circuit_breaker_window_seconds: int = 60
    ai_circuit_breaker_cooldown_seconds: int = 120
    log_exporter: str | None = None  # "loki", "cloudwatch", None
    loki_endpoint: str | None = None
    loki_basic_auth: str | None = None  # user:pass
    cloudwatch_log_group: str | None = None
    cloudwatch_log_stream: str | None = None
    oidc_issuer: str | None = None
    oidc_client_id: str | None = None
    oidc_admin_allowed_domain: str | None = None
    admin_api_token: str | None = Field(
        default=None, validation_alias=AliasChoices("ADMIN_API_TOKEN", "ADMIN_API_KEY")
    )


def _env_file_mtime(path: str | None) -> float:
    if not path:
        return -1.0
    try:
        return Path(path).stat().st_mtime
    except Exception:
        return -1.0


def _get_settings_uncached(*, env_file: str | None) -> Settings:
    if env_file:
        # Forzar lectura del env file actual (útil en local cuando cambian claves sin reinicio).
        return Settings(_env_file=env_file)
    return Settings()


# Cache con invalidación automática por mtime del env_file para evitar confusión en local
# (p.ej., cambio de OPENAI_API_KEY sin reiniciar el backend).
from functools import lru_cache  # noqa: E402


@lru_cache(maxsize=4)
def _get_settings_cached(env_file: str | None, mtime: float) -> Settings:
    return _get_settings_uncached(env_file=env_file)


def get_settings() -> Settings:
    env_file = _resolve_env_file()
    mtime = _env_file_mtime(env_file)
    return _get_settings_cached(env_file, mtime)
