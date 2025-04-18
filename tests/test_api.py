import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_tao_dividends():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/tao_dividends", headers={"Authorization": "Bearer some_secret_auth_token"})
        assert response.status_code == 200
