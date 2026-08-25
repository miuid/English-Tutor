import json
import os
from unittest.mock import AsyncMock, Mock, patch

import anthropic
import httpx
import pytest

from app.config import Settings
from app.llm import FakeProvider, StageProviderRouter, create_llm_provider
from app.llm.deepseek import API_URL, DeepSeekProvider
from app.llm.kimi import API_URL as KIMI_API_URL
from app.llm.kimi import KimiProvider


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


def _deepseek_settings() -> Settings:
    return Settings(
        llm_provider="deepseek",
        llm_model="deepseek-chat",
        llm_api_key="test-key",
    )


def test_factory_returns_deepseek_provider() -> None:
    provider = create_llm_provider(_deepseek_settings())
    assert isinstance(provider, DeepSeekProvider)


def test_deepseek_provider_requires_api_key() -> None:
    settings = Settings(llm_provider="fake", llm_model="deepseek-chat", llm_api_key="")
    with pytest.raises(ValueError, match="LLM_API_KEY is required for DeepSeekProvider"):
        DeepSeekProvider(settings)


@pytest.mark.asyncio
async def test_deepseek_provider_request_shape_and_content() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["authorization"]
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "mocked reply"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = DeepSeekProvider(_deepseek_settings(), client=client)

    result = await provider.generate(
        "system prompt",
        [{"role": "user", "content": "hello"}],
    )

    assert result == "mocked reply"
    assert captured["url"] == API_URL
    assert captured["authorization"] == "Bearer test-key"
    body = captured["json"]
    assert isinstance(body, dict)
    assert body["model"] == "deepseek-chat"
    assert body["stream"] is False
    assert body["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "hello"},
    ]


@pytest.mark.asyncio
async def test_deepseek_provider_raises_clear_error_on_http_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limit exceeded")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = DeepSeekProvider(_deepseek_settings(), client=client)

    with pytest.raises(RuntimeError, match="status 429: rate limit exceeded"):
        await provider.generate("system", [{"role": "user", "content": "hi"}])


def _kimi_settings() -> Settings:
    return Settings(
        llm_provider="kimi",
        llm_model="kimi-k3",
        llm_api_key="test-key",
    )


def test_factory_returns_kimi_provider() -> None:
    provider = create_llm_provider(_kimi_settings())
    assert isinstance(provider, KimiProvider)


def test_kimi_provider_requires_api_key() -> None:
    settings = Settings(llm_provider="fake", llm_model="kimi-k3", llm_api_key="")
    with pytest.raises(ValueError, match="LLM_API_KEY is required for KimiProvider"):
        KimiProvider(settings)


@pytest.mark.asyncio
async def test_kimi_provider_request_shape_and_content() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["authorization"]
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "mocked reply"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = KimiProvider(_kimi_settings(), client=client)

    result = await provider.generate(
        "system prompt",
        [{"role": "user", "content": "hello"}],
    )

    assert result == "mocked reply"
    assert captured["url"] == KIMI_API_URL
    assert captured["authorization"] == "Bearer test-key"
    body = captured["json"]
    assert isinstance(body, dict)
    assert body["model"] == "kimi-k3"
    assert body["stream"] is False
    assert body["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "hello"},
    ]


@pytest.mark.asyncio
async def test_kimi_provider_raises_clear_error_on_http_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limit exceeded")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = KimiProvider(_kimi_settings(), client=client)

    with pytest.raises(RuntimeError, match="status 429: rate limit exceeded"):
        await provider.generate("system", [{"role": "user", "content": "hi"}])


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


@pytest.mark.skipif(
    os.environ.get("LLM_PROVIDER") != "deepseek" or not os.environ.get("LLM_API_KEY"),
    reason="Real LLM test requires LLM_PROVIDER=deepseek and LLM_API_KEY",
)
@pytest.mark.asyncio
async def test_real_deepseek_returns_completion() -> None:
    settings = Settings()
    provider = create_llm_provider(settings)
    response = await provider.generate(
        "You are a helpful English tutor.",
        [{"role": "user", "content": "Say 'hello' and nothing else."}],
    )
    assert response
    assert "hello" in response.lower()


def _routed_settings() -> Settings:
    return Settings(
        llm_provider="fake",
        llm_model="fake-base",
        llm_api_key="",
        llm_stage_models={"end": "fake-strong", "coach": "fake-strong"},
    )


def test_router_returns_default_model_for_unmapped_stage() -> None:
    router = StageProviderRouter(_routed_settings())
    provider, model = router.for_stage("retrieval")
    assert isinstance(provider, FakeProvider)
    assert model == "fake-base"


def test_router_returns_stage_override_for_mapped_stage() -> None:
    router = StageProviderRouter(_routed_settings())
    provider, model = router.for_stage("end")
    assert isinstance(provider, FakeProvider)
    assert model == "fake-strong"


def test_router_caches_provider_per_stage() -> None:
    router = StageProviderRouter(_routed_settings())
    assert router.for_stage("end")[0] is router.for_stage("end")[0]
    assert router.for_stage("end")[0] is not router.for_stage("retrieval")[0]


def test_router_applies_model_override_to_real_provider() -> None:
    settings = Settings(
        llm_provider="kimi",
        llm_model="kimi-k3",
        llm_api_key="test-key",
        llm_stage_models={"retrieval": "kimi-k3-mini"},
    )
    router = StageProviderRouter(settings)
    provider, model = router.for_stage("retrieval")
    assert isinstance(provider, KimiProvider)
    assert model == "kimi-k3-mini"
    default_provider, default_model = router.for_stage("start")
    assert isinstance(default_provider, KimiProvider)
    assert default_model == "kimi-k3"


def test_get_executor_without_routing_table_keeps_single_provider() -> None:
    """Empty routing table -> no router; the injected provider is used as-is."""
    from app.api.deps import get_executor

    settings = Settings(llm_provider="fake", llm_model="fake-base", llm_api_key="")
    provider = FakeProvider()
    executor = get_executor(provider=provider, settings=settings)
    assert executor.stage_router is None
    assert executor.provider is provider


def test_get_executor_with_routing_table_builds_router() -> None:
    from app.api.deps import get_executor

    settings = Settings(
        llm_provider="fake",
        llm_model="fake-base",
        llm_api_key="",
        llm_stage_models={"end": "fake-strong"},
    )
    executor = get_executor(provider=FakeProvider(), settings=settings)
    assert executor.stage_router is not None
    assert executor.stage_router.for_stage("end")[1] == "fake-strong"
