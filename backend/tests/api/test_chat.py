from httpx import AsyncClient

from tests.conftest import sign_up


def _parse_sse_events(raw: str) -> list[tuple[str, str]]:
    events = []
    for block in raw.strip().split("\n\n"):
        lines = block.splitlines()
        event = next(line.removeprefix("event: ") for line in lines if line.startswith("event: "))
        data = next(line.removeprefix("data: ") for line in lines if line.startswith("data: "))
        events.append((event, data))
    return events


async def test_chat_streams_sse_events_and_persists_messages(client: AsyncClient) -> None:
    await sign_up(client, "chatter@example.com")
    conversation = (await client.post("/api/v1/conversations", json={})).json()

    response = await client.post(
        "/api/v1/chat",
        json={"conversation_id": conversation["id"], "content": "Hello there"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = _parse_sse_events(response.text)
    event_names = [name for name, _ in events]

    assert event_names[0] == "message_start"
    assert "content_delta" in event_names
    assert event_names[-1] == "message_complete"

    messages_response = await client.get(f"/api/v1/conversations/{conversation['id']}/messages")
    messages = messages_response.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello there"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["status"] == "complete"
    assert messages[1]["content"].strip() == "This is a test reply."


async def test_chat_rejects_unknown_conversation(client: AsyncClient) -> None:
    await sign_up(client, "chatter2@example.com")
    response = await client.post(
        "/api/v1/chat",
        json={"conversation_id": "00000000-0000-0000-0000-000000000000", "content": "Hi"},
    )
    assert response.status_code == 200  # SSE already started; error arrives as an event
    events = _parse_sse_events(response.text)
    assert events[0][0] == "error"


async def test_chat_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/chat",
        json={"conversation_id": "00000000-0000-0000-0000-000000000000", "content": "Hi"},
    )
    assert response.status_code == 401
