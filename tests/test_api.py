import pytest
from fastapi import status
from unittest.mock import patch


@pytest.mark.asyncio
async def test_tao_dividends_no_auth(client):
    """Test unauthorized access returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/api/v1/tao_dividends", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid or missing Authorization header"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "trade_param, should_trigger_celery",
    [
        (True, True),
        (False, False),
    ],
)
@patch("app.tasks.bittensor.perform_trade_task.delay")
@patch("app.api.v1.routes.get_dividends", return_value=[])
async def test_tao_dividends_with_auth(
    mock_get_dividends,
    mock_celery_delay,
    trade_param,
    should_trigger_celery,
    mocker,
    client,
):
    """Test authenticated access with optional trade parameter triggers background tasks correctly."""
    mocker.patch("app.auth.auth.settings.auth_token", "test")

    headers = {"Authorization": "Bearer test"}
    url = f"/api/v1/tao_dividends?trade={'true' if trade_param else 'false'}"

    response = client.get(url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

    mock_get_dividends.assert_called_once()

    if should_trigger_celery:
        mock_celery_delay.assert_called_once()
    else:
        mock_celery_delay.assert_not_called()
