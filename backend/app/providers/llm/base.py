from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ChatMessage:
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass(frozen=True)
class StreamEvent:
    type: Literal["delta", "done"]
    text: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMProvider(ABC):
    """Adapter interface for chat-completion providers.

    Only this module's implementations should import a provider SDK directly,
    so swapping providers never touches call sites in services/routers.
    """

    @abstractmethod
    def stream_chat(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> AsyncGenerator[StreamEvent]:
        """Yield StreamEvent("delta", ...) chunks, ending implicitly when exhausted."""

    @abstractmethod
    async def complete_chat(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> str:
        """Return the full completion text without streaming (used internally/in tests)."""
