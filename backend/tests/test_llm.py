import os
from unittest.mock import AsyncMock, Mock, patch

import anthropic
import pytest

from app.config import Settings
from app.llm import FakeProvider, create_llm_provider


@pytest.mark.asyncio
async def test_fake_provider_returns_canned_text() -> None:
    provider = FakeProvider(canned_responses=["Hello, student!"])
    response = await provider.generate(
        system_prompt="You are a tutor.",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert response == "Hello, student!"


@pytest.mark.asyncio
async def test_factory_returns_fake_provider() -> None:
    settings = Settings(
        llm_provider="fake",
        llm_model="fake-model",
        llm_api_key="",
    )
    provider = create_llm_provider(settings)
    assert isinstance(provider, FakeProvider)
    response = await provider.generate("system", [{"role": "user", "content": "hi"}])
    assert response == "fake response"


def test_factory_raises_on_unknown_provider() -> None:
    settings = Settings(
        llm_provider="unknown",
        llm_model="unknown",
        llm_api_key="some-key",
    )
    with pytest.raises(ValueError, match="Unsupported LLM provider: unknown"):
        create_llm_provider(settings)


@pytest.mark.asyncio
async def test_anthropic_provider_calls_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("anthropic")
    from app.llm.anthropic import AnthropicProvider

    settings = Settings(
        llm_provider="anthropic",
        llm_model="claude-sonnet-4-6",
        llm_api_key="test-key",
    )
    provider = AnthropicProvider(settings)

    fake_block = anthropic.types.TextBlock(text="mocked response", type="text")
    fake_response = Mock()
    fake_response.content = [fake_block]

    with patch.object(
        provider.client.messages,
        "create",
        new=AsyncMock(return_value=fake_response),
    ):
        response = await provider.generate(
            "system prompt",
            [{"role": "user", "content": "hello"}],
        )
        assert response == "mocked response"


@pytest.mark.skipif(
    os.environ.get("LLM_PROVIDER") != "anthropic" or not os.environ.get("LLM_API_KEY"),
    reason="Real LLM test requires LLM_PROVIDER=anthropic and LLM_API_KEY",
)
@pytest.mark.asyncio
async def test_real_llm_returns_completion() -> None:
    settings = Settings()
    provider = create_llm_provider(settings)
    response = await provider.generate(
        "You are a helpful English tutor.",
        [{"role": "user", "content": "Say 'hello' and nothing else."}],
    )
    assert response
    assert "hello" in response.lower()
