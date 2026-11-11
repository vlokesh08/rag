from httpx import AsyncClient

from tests.conftest import sign_up


async def test_create_and_list_knowledge_bases(client: AsyncClient) -> None:
    await sign_up(client, "owner@example.com")

    create_response = await client.post(
        "/api/v1/knowledge-bases", json={"name": "Docs", "description": "desc"}
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Docs"

    list_response = await client.get("/api/v1/knowledge-bases")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == created["id"]


async def test_get_update_delete_knowledge_base(client: AsyncClient) -> None:
    await sign_up(client, "owner2@example.com")
    created = (
        await client.post("/api/v1/knowledge-bases", json={"name": "Docs"})
    ).json()

    get_response = await client.get(f"/api/v1/knowledge-bases/{created['id']}")
    assert get_response.status_code == 200

    patch_response = await client.patch(
        f"/api/v1/knowledge-bases/{created['id']}", json={"name": "Renamed"}
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Renamed"

    delete_response = await client.delete(f"/api/v1/knowledge-bases/{created['id']}")
    assert delete_response.status_code == 204

    get_after_delete = await client.get(f"/api/v1/knowledge-bases/{created['id']}")
    assert get_after_delete.status_code == 404


async def test_unauthenticated_requests_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/v1/knowledge-bases")
    assert response.status_code == 401


async def test_user_cannot_access_another_users_knowledge_base(client: AsyncClient) -> None:
    await sign_up(client, "userA@example.com")
    created = (
        await client.post("/api/v1/knowledge-bases", json={"name": "A's KB"})
    ).json()
    kb_id = created["id"]

    # Sign out of A, sign in as B on the same client (shared cookie jar).
    await client.post("/api/v1/auth/sign-out")
    await sign_up(client, "userB@example.com")

    get_response = await client.get(f"/api/v1/knowledge-bases/{kb_id}")
    assert get_response.status_code == 404

    patch_response = await client.patch(
        f"/api/v1/knowledge-bases/{kb_id}", json={"name": "Hijacked"}
    )
    assert patch_response.status_code == 404

    delete_response = await client.delete(f"/api/v1/knowledge-bases/{kb_id}")
    assert delete_response.status_code == 404

    list_response = await client.get("/api/v1/knowledge-bases")
    assert list_response.json() == []
