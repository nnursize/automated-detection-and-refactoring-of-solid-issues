"""Abstract LLM provider interface."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

from ..models import LLMResponse


class LLMProvider(ABC):
    """Base class for LLM API providers."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send a prompt to the LLM and return the response."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'gemini', 'groq')."""
        ...

    @abstractmethod
    def max_context_tokens(self) -> int:
        """Maximum context window size in tokens."""
        ...

    def complete_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> LLMResponse:
        """Call complete() with exponential backoff on failure.

        For 429 rate-limit errors, extracts the suggested retry delay from the
        error message and waits that long before retrying.
        """
        import re

        last_error = None
        for attempt in range(max_retries):
            try:
                return self.complete(system_prompt, user_prompt, temperature, max_tokens)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    error_str = str(e)
                    # Check for 429 rate limit and extract suggested wait time
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        # Try to parse "retry in Xs" from the error
                        match = re.search(r"retry[^\d]*(\d+)", error_str, re.IGNORECASE)
                        wait = int(match.group(1)) + 5 if match else 60
                        print(f"  Rate limit hit. Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                    else:
                        wait = 2 ** (attempt + 1)  # 2, 4, 8 seconds
                        print(f"  Retry {attempt + 1}/{max_retries} after {wait}s: {e}")
                    time.sleep(wait)
        raise RuntimeError(
            f"LLM call failed after {max_retries} retries: {last_error}"
        )
