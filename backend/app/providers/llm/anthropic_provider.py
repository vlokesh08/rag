from collections.abc import AsyncGenerator
from typing import Any, cast

from anthropic import AsyncAnthropic

from app.core.config import settings
from app.providers.llm.base import ChatMessage, LLMProvider, StreamEvent


def _split_system(messages: list[ChatMessage]) -> tuple[str | None, list[ChatMessage]]:
    system_parts = [m.content for m in messages if m.role == "system"]
    rest = [m for m in messages if m.role != "system"]
    return ("\n\n".join(system_parts) or None, rest)


def _to_provider_messages(messages: list[ChatMessage]) -> Any:
    # The Anthropic SDK's MessageParam TypedDict union is awkward to satisfy
    # structurally from a plain dict comprehension; `rest` is already
    # guaranteed (by `_split_system`) to contain only user/assistant roles.
    return [{"role": m.role, "content": m.content} for m in messages]


class AnthropicProvider(LLMProvider):
    """The only module that imports the `anthropic` SDK."""

    def __init__(self) -> None:
        self._client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.anthropic_timeout_seconds,
        )

    async def stream_chat(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> AsyncGenerator[StreamEvent]:
        system, rest = _split_system(messages)
        async with self._client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=max_tokens or settings.anthropic_max_tokens,
            system=system or "",
            messages=_to_provider_messages(rest),
        ) as stream:
            async for text in stream.text_stream:
                yield StreamEvent(type="delta", text=text)
            final = await stream.get_final_message()
            yield StreamEvent(
                type="done",
                input_tokens=final.usage.input_tokens,
                output_tokens=final.usage.output_tokens,
            )

    async def complete_chat(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> str:
        system, rest = _split_system(messages)
        response = await self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens or settings.anthropic_max_tokens,
            system=system or "",
            messages=_to_provider_messages(rest),
        )
        return "".join(
            cast(str, block.text) for block in response.content if block.type == "text"
        )
