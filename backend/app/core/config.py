from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="", extra="ignore", case_sensitive=False
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
    panel_api_token: str | None = None
    storage_dir: str = "/tmp/chatbot_uploads"
    cors_origins: str | None = None  # comma-separated
    rate_limit_per_min: int = 120
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_exp_hours: int = 24
    ai_price_per_token_usd: float = 0.000002


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
