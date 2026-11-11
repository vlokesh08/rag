from httpx import AsyncClient

from tests.conftest import sign_up


async def test_create_and_list_conversations(client: AsyncClient) -> None:
    await sign_up(client, "owner@example.com")

    create_response = await client.post("/api/v1/conversations", json={"title": "First chat"})
    assert create_response.status_code == 201
    created = create_response.json()

    list_response = await client.get("/api/v1/conversations")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == created["id"]


async def test_get_and_delete_conversation(client: AsyncClient) -> None:
    await sign_up(client, "owner2@example.com")
    created = (await client.post("/api/v1/conversations", json={})).json()

    get_response = await client.get(f"/api/v1/conversations/{created['id']}")
    assert get_response.status_code == 200

    delete_response = await client.delete(f"/api/v1/conversations/{created['id']}")
    assert delete_response.status_code == 204

    get_after_delete = await client.get(f"/api/v1/conversations/{created['id']}")
    assert get_after_delete.status_code == 404


async def test_list_messages_empty_initially(client: AsyncClient) -> None:
    await sign_up(client, "owner3@example.com")
    created = (await client.post("/api/v1/conversations", json={})).json()

    messages_response = await client.get(f"/api/v1/conversations/{created['id']}/messages")
    assert messages_response.status_code == 200
    assert messages_response.json() == []


async def test_user_cannot_access_another_users_conversation(client: AsyncClient) -> None:
    await sign_up(client, "userA@example.com")
    created = (await client.post("/api/v1/conversations", json={"title": "A's chat"})).json()
    conversation_id = created["id"]

    await client.post("/api/v1/auth/sign-out")
    await sign_up(client, "userB@example.com")

    get_response = await client.get(f"/api/v1/conversations/{conversation_id}")
    assert get_response.status_code == 404

    messages_response = await client.get(f"/api/v1/conversations/{conversation_id}/messages")
    assert messages_response.status_code == 404

    delete_response = await client.delete(f"/api/v1/conversations/{conversation_id}")
    assert delete_response.status_code == 404

    list_response = await client.get("/api/v1/conversations")
    assert list_response.json() == []
