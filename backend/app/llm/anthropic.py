"""Anthropic LLM provider adapter."""

from typing import cast

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, TextBlock

from app.config import Settings
from app.llm.provider import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.model = settings.llm_model
        if not settings.llm_api_key:
            msg = "LLM_API_KEY is required for AnthropicProvider"
            raise ValueError(msg)
        self.client = AsyncAnthropic(api_key=settings.llm_api_key)

    async def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        typed_messages = cast(list[MessageParam], messages)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=typed_messages,
        )
        first_block = response.content[0]
        if isinstance(first_block, TextBlock):
            return first_block.text
        msg = f"Unexpected response content type: {type(first_block)}"
        raise RuntimeError(msg)
