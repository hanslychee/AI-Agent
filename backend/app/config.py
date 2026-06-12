"""Application configuration loaded from environment variables / .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    ai_model: str = "claude-opus-4-8"

    secret_key: str = "change-me-to-a-long-random-string"
    access_token_expire_minutes: int = 60 * 12

    admin_username: str = "admin"
    admin_password: str = "admin123"

    database_url: str = "sqlite:///./recruitai.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
