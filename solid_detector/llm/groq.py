"""Groq LLM provider."""

from __future__ import annotations

import time

from groq import Groq

from ..models import LLMResponse
from .base import LLMProvider


class GroqProvider(LLMProvider):
    """Groq API provider (free tier, fast inference)."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self._client = Groq(api_key=api_key)
        self._model = model

    def name(self) -> str:
        return "groq"

    def max_context_tokens(self) -> int:
        return 128_000

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        start = time.time()

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency_ms = (time.time() - start) * 1000

        usage = response.usage
        return LLMResponse(
            raw_text=response.choices[0].message.content or "",
            model=self._model,
            provider="groq",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
            finish_reason=response.choices[0].finish_reason or "",
        )
