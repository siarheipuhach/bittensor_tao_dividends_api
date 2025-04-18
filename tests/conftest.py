import pytest
from app.config import Settings

@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    monkeypatch.setattr("app.config.settings", Settings(
        auth_token="test",
        redis_url="redis://localhost:6379",
        chutes_api_key="fake-chutes",
        datura_api_key="fake-datura"
    ))
