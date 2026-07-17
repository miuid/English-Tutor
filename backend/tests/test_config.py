import os
from unittest.mock import patch

import pytest

from app.config import Settings


def test_settings_defaults() -> None:
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings(llm_provider="fake")
    assert settings.app_env == "development"
    assert settings.llm_model == "deepseek-chat"
    assert settings.database_url == "sqlite:///./english_tutor.db"
    assert settings.llm_api_key is None


def test_default_provider_is_deepseek() -> None:
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings(llm_api_key="dummy")
    assert settings.llm_provider == "deepseek"


def test_settings_load_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_MODEL", "fake-model")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("APP_ENV", "testing")
    settings = Settings()
    assert settings.llm_provider == "fake"
    assert settings.llm_model == "fake-model"
    assert settings.database_url == "sqlite:///test.db"
    assert settings.app_env == "testing"


def test_missing_api_key_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(
        ValueError,
        match="LLM_API_KEY is required when LLM_PROVIDER='anthropic'",
    ):
        Settings()


def test_default_deepseek_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(
        ValueError,
        match="LLM_API_KEY is required when LLM_PROVIDER='deepseek'",
    ):
        Settings()


def test_fake_provider_does_not_require_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    settings = Settings()
    assert settings.llm_provider == "fake"
    assert settings.llm_api_key is None
