from httpx import AsyncClient

from tests.conftest import sign_up


async def test_sign_up_creates_session_and_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/sign-up", json={"email": "alice@example.com", "password": "supersecret1"}
    )
    assert response.status_code == 201
    assert response.json()["user"]["email"] == "alice@example.com"
    assert "rag_session" in response.cookies


async def test_sign_up_duplicate_email_conflicts(client: AsyncClient) -> None:
    await sign_up(client, "bob@example.com")
    response = await client.post(
        "/api/v1/auth/sign-up", json={"email": "bob@example.com", "password": "anotherpass"}
    )
    assert response.status_code == 409


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_returns_current_user_after_sign_up(client: AsyncClient) -> None:
    user = await sign_up(client, "carol@example.com")
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


async def test_sign_in_with_wrong_password_rejected(client: AsyncClient) -> None:
    await sign_up(client, "dave@example.com")
    response = await client.post(
        "/api/v1/auth/sign-in", json={"email": "dave@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


async def test_sign_out_invalidates_session(client: AsyncClient) -> None:
    await sign_up(client, "erin@example.com")
    sign_out_response = await client.post("/api/v1/auth/sign-out")
    assert sign_out_response.status_code == 204

    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 401
