from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Mapping

from .providers import LLMProvider


@dataclass(frozen=True)
class AgentOutput:
    role: str
    content: str
    inputs: tuple[str, ...]


class PromptRegistry:
    def __init__(self) -> None:
        path = files("mel_governor").joinpath("prompts.json")
        self._prompts: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))

    def get(self, role: str) -> str:
        try:
            return self._prompts[role]
        except KeyError as exc:
            raise KeyError(f"Unknown agent role: {role}") from exc

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(self._prompts)


class ResearchAgent:
    def __init__(self, role: str, provider: LLMProvider, registry: PromptRegistry) -> None:
        self.role = role
        self.provider = provider
        self.system_prompt = registry.get(role)

    def run(self, *, question: str, context: Mapping[str, str]) -> AgentOutput:
        ordered = "\n\n".join(f"## {key}\n{value}" for key, value in sorted(context.items()))
        user_prompt = f"Research question:\n{question}\n\nAvailable context:\n{ordered or '[none]'}"
        content = self.provider.complete(
            role=self.role,
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )
        return AgentOutput(self.role, content, tuple(sorted(context)))
