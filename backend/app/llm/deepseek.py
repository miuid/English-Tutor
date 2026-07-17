"""DeepSeek LLM provider adapter (OpenAI-compatible HTTP API)."""

from typing import Any

import httpx

from app.config import Settings
from app.llm.provider import LLMProvider

API_URL = "https://api.deepseek.com/chat/completions"
REQUEST_TIMEOUT = 60.0
ERROR_BODY_SNIPPET = 300


class DeepSeekProvider(LLMProvider):
    """Call DeepSeek's OpenAI-compatible chat completions endpoint over HTTP."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.model = settings.llm_model
        if not settings.llm_api_key:
            msg = "LLM_API_KEY is required for DeepSeekProvider"
            raise ValueError(msg)
        self._api_key = settings.llm_api_key
        # Optional injected client (tests); otherwise one is created per call.
        self._client = client

    async def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "stream": False,
        }
        if self._client is not None:
            return await self._send(self._client, payload)
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            return await self._send(client, payload)

    async def _send(self, client: httpx.AsyncClient, payload: dict[str, Any]) -> str:
        response = await client.post(
            API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
        if response.status_code != 200:
            snippet = response.text[:ERROR_BODY_SNIPPET]
            msg = f"DeepSeek API request failed with status {response.status_code}: {snippet}"
            raise RuntimeError(msg)
        content = response.json()["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            msg = "DeepSeek API response is missing choices[0].message.content"
            raise RuntimeError(msg)
        return content
