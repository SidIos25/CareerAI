from __future__ import annotations

import json
import logging
import os
from typing import Any

from litellm import acompletion


logger = logging.getLogger(__name__)


class RootAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.2) -> None:
        configured_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.model = configured_model if "/" in configured_model else f"openai/{configured_model}"
        self.temperature = temperature
        self.timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "45"))
        self.max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "1"))
        self.top_p = float(os.getenv("OPENAI_TOP_P", "0.1"))

    async def ask_json(self, system_prompt: str, user_prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        safe_fallback = dict(fallback)
        try:
            response = await acompletion(
                model=self.model,
                temperature=self.temperature,
                top_p=self.top_p,
                timeout=self.timeout_seconds,
                num_retries=self.max_retries,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = self._extract_content(response)
        except Exception as exc:
            logger.warning("LLM call failed; returning fallback. error=%s", exc)
            return safe_fallback

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
            return safe_fallback
        except json.JSONDecodeError:
            cleaned = self._strip_markdown_fences(content)
            if cleaned != content:
                try:
                    reparsed = json.loads(cleaned)
                    if isinstance(reparsed, dict):
                        return reparsed
                except json.JSONDecodeError:
                    pass
            logger.warning("JSON parse failed; returning fallback.")
            return safe_fallback

    @staticmethod
    def _extract_content(response: Any) -> str:
        choices = getattr(response, "choices", None) or []
        if not choices:
            return "{}"
        message = getattr(choices[0], "message", None)
        if message is None:
            return "{}"

        content = getattr(message, "content", None)
        if content is None:
            return "{}"
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict):
                    text_value = item.get("text")
                    if isinstance(text_value, str):
                        text_parts.append(text_value)
            return "\n".join(text_parts) if text_parts else "{}"
        return str(content)

    @staticmethod
    def _strip_markdown_fences(content: str) -> str:
        text = content.strip()
        if not text.startswith("```"):
            return text

        lines = text.splitlines()
        if not lines:
            return text
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
