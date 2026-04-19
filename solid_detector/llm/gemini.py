"""Google Gemini LLM provider (using google-genai SDK)."""

from __future__ import annotations

import time

from google import genai
from google.genai import types

from ..models import LLMResponse
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini API provider (free tier)."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self._client = genai.Client(api_key=api_key)
        self._model_name = model

    def name(self) -> str:
        return "gemini"

    def list_models(self, text_only: bool = True) -> list[str]:
        """Return IDs of models that support generateContent for this API key.

        When text_only is True, drop models that aren't useful for this project
        (image, tts, robotics, computer-use, etc.).
        """
        skip_tokens = (
            "image", "tts", "robotics", "computer-use", "customtools",
            "clip", "nano-banana", "lyria", "deep-research",
        )
        ids = []
        for m in self._client.models.list():
            actions = getattr(m, "supported_actions", None) or getattr(
                m, "supported_generation_methods", None
            ) or []
            if actions and "generateContent" not in actions:
                continue
            mid = m.name.replace("models/", "")
            if text_only and any(tok in mid for tok in skip_tokens):
                continue
            ids.append(mid)
        return sorted(ids)

    def max_context_tokens(self) -> int:
        return 1_000_000  # Gemini 2.5 Flash supports 1M tokens

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        start = time.time()

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )

        latency_ms = (time.time() - start) * 1000

        # Extract usage metadata
        prompt_tokens = 0
        completion_tokens = 0
        if response.usage_metadata:
            prompt_tokens = response.usage_metadata.prompt_token_count or 0
            completion_tokens = response.usage_metadata.candidates_token_count or 0

        return LLMResponse(
            raw_text=response.text or "",
            model=self._model_name,
            provider="gemini",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            finish_reason=str(
                response.candidates[0].finish_reason
            ) if response.candidates else "",
        )
