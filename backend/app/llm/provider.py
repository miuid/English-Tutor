from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Common interface for all LLM backends."""

    async def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        """Generate a text completion from the LLM."""
        ...
