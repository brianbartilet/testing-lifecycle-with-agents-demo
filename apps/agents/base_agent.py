"""
Base agent class for the AI-driven testing lifecycle.

All agents extend this class, which provides:
- Direct Anthropic SDK access (no harqis-core config dependency)
- Exponential backoff retry logic
- Structured output writing helpers
- Token-aware generation with large max_tokens for code output
"""
import os
import re
import time
import random
from pathlib import Path
from typing import Optional

from anthropic import Anthropic, RateLimitError, APIConnectionError, InternalServerError
from core.utilities.logging.custom_logger import logger as log


class BaseAgent:
    """
    Base class for all testing lifecycle agents.

    Subclasses implement `run()` which calls `_ask()` with a prompt and
    returns the generated artifact (feature file, test code, etc.).
    """

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 8096
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0
    RETRY_MAX_DELAY = 60.0

    _RETRYABLE = (RateLimitError, APIConnectionError, InternalServerError)

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Export it before running the agents."
            )
        self._client = Anthropic(api_key=self.api_key, max_retries=0)

    def _ask(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a prompt to Claude and return the text response.

        Retries on rate limits and transient errors with exponential backoff.
        """
        payload = {
            "model": self.MODEL,
            "max_tokens": max_tokens or self.MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        last_exc = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = self._client.messages.create(**payload)
                return response.content[0].text
            except self._RETRYABLE as exc:
                last_exc = exc
                if attempt == self.MAX_RETRIES:
                    break
                delay = min(
                    self.RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1),
                    self.RETRY_MAX_DELAY,
                )
                log.warning(
                    f"[{self.__class__.__name__}] Retryable error "
                    f"(attempt {attempt + 1}/{self.MAX_RETRIES}) — retry in {delay:.1f}s: {exc}"
                )
                time.sleep(delay)
        raise last_exc

    @staticmethod
    def _extract_code_block(text: str, lang: str = "") -> str:
        """
        Extract content from a markdown code block if present.

        Falls back to the raw text if no code block markers are found.
        """
        pattern = rf"```{re.escape(lang)}\s*\n(.*?)```" if lang else r"```(?:\w+)?\s*\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: strip any leading/trailing code fences
        cleaned = re.sub(r"^```\w*\n?", "", text.strip())
        cleaned = re.sub(r"\n?```$", "", cleaned)
        return cleaned.strip()

    @staticmethod
    def write_file(path: str, content: str) -> None:
        """Write content to a file, creating parent directories as needed."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        log.info(f"Written: {path}")

    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement run()")
