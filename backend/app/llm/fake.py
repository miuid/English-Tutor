from dataclasses import dataclass, field

from app.llm.provider import LLMProvider


@dataclass
class FakeProvider(LLMProvider):
    """Canned LLM provider for unit tests and offline demos."""

    canned_responses: list[str] = field(default_factory=list)
    _call_count: int = field(init=False, default=0)
    calls: list[tuple[str, list[dict[str, str]]]] = field(default_factory=list)

    async def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        self.calls.append((system_prompt, messages))
        if self.canned_responses:
            response = self.canned_responses[self._call_count % len(self.canned_responses)]
            self._call_count += 1
            return response
        return "fake response"
