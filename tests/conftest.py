from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import async_session
from app.main import app


import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def db_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    monkeypatch.setattr(
        "app.config.settings",
        Settings(
            auth_token="test",
            redis_url="redis://localhost:6379",
            chutes_api_key="fake-chutes",
            datura_api_key="fake-datura",
        ),
    )


@pytest.fixture
def mock_httpx_client(mocker):
    mock_client = mocker.patch("httpx.AsyncClient", autospec=True)
    mock_instance = mock_client.return_value
    mock_aenter = AsyncMock()
    mock_instance.__aenter__.return_value = mock_aenter
    return mock_aenter
