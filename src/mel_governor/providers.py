from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    name: str

    def complete(self, *, role: str, system_prompt: str, user_prompt: str) -> str:
        ...


@dataclass(frozen=True)
class MockProvider:
    """Deterministic offline provider used for tests and architecture validation."""

    name: str = "mock"

    def complete(self, *, role: str, system_prompt: str, user_prompt: str) -> str:
        digest = hashlib.sha256(
            f"{role}\n{system_prompt}\n{user_prompt}".encode("utf-8")
        ).hexdigest()[:16]
        return (
            f"[OFFLINE MOCK {digest}] role={role}. "
            "This deterministic output validates orchestration only; it is not a "
            "substantive political or research conclusion. Human review required."
        )


class GroqProvider:
    name = "groq"

    def __init__(self, model: str = "llama-3.3-70b-versatile") -> None:
        key = os.getenv("GROQ_API_KEY", "").strip()
        if not key:
            raise ProviderError("GROQ_API_KEY is required when MEL_LLM_PROVIDER=groq")
        try:
            from groq import Groq
        except ImportError as exc:
            raise ProviderError("Install the optional 'groq' dependency") from exc
        self._client = Groq(api_key=key)
        self._model = model

    def complete(self, *, role: str, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )
        return response.choices[0].message.content or ""


def provider_from_env() -> LLMProvider:
    provider = os.getenv("MEL_LLM_PROVIDER", "mock").strip().lower()
    if provider == "mock":
        return MockProvider()
    if provider == "groq":
        return GroqProvider()
    raise ProviderError(f"Unsupported MEL_LLM_PROVIDER: {provider}")
