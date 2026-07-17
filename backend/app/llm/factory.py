from app.config import Settings
from app.llm.anthropic import AnthropicProvider
from app.llm.fake import FakeProvider
from app.llm.provider import LLMProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Return a provider instance based on config."""
    if settings.llm_provider == "anthropic":
        return AnthropicProvider(settings)
    if settings.llm_provider == "fake":
        return FakeProvider()
    msg = f"Unsupported LLM provider: {settings.llm_provider}"
    raise ValueError(msg)
