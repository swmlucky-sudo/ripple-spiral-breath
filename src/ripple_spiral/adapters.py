from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, Any


class LLMAdapter(Protocol):
    """You implement this to call your actual model (OpenAI, local, etc.)."""

    def generate(self, prompt: str, *, meta: Dict[str, Any] | None = None) -> str:
        ...


@dataclass
class DummyAdapter:
    """A minimal adapter for local testing."""
    echo: bool = True

    def generate(self, prompt: str, *, meta: Dict[str, Any] | None = None) -> str:
        if self.echo:
            return f"[dummy] {prompt[:200]}"
        return "[dummy]"
