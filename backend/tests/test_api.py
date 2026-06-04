import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_jobs_no_cache(client):
    response = await client.get("/jobs", params={"location": "Nowhere, XX"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scrape_invalid_location(client):
    response = await client.post("/scrape", params={"location": "Xyzzzzzzzz"})
    assert response.status_code in (200, 502)
