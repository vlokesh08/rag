from httpx import AsyncClient


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_worker_ping_enqueues_job(client: AsyncClient) -> None:
    response = await client.post("/api/v1/health/worker-ping")
    assert response.status_code == 200
    assert response.json() == {"job_id": "fake-job-id"}
