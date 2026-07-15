"""Application settings loaded from environment / .env file."""

from functools import lru_cache

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = "sqlite:///./english_tutor.db"
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    llm_api_key: str | None = None

    @field_validator("llm_api_key")
    @classmethod
    def require_key_for_real_providers(
        cls,
        value: str | None,
        info: ValidationInfo,
    ) -> str | None:
        provider = info.data.get("llm_provider", "anthropic")
        if provider != "fake" and not value:
            msg = f"LLM_API_KEY is required when LLM_PROVIDER='{provider}'"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    `get_settings()` is the single source of truth for runtime settings. The
    cache means repeated calls are cheap, but tests can call `cache_clear()`
    when they need to reload from a changed environment.
    """
    return Settings()
