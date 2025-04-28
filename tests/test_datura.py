import pytest
import datetime
from unittest.mock import AsyncMock

from app.services.datura import search_twitter_subnet_mentions


@pytest.mark.asyncio
async def test_search_twitter_subnet_mentions(mock_httpx_client):
    # Mock response properly
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=[{"text": "Subnet is booming!"}])
    mock_response.raise_for_status = lambda: None

    mock_httpx_client.get.return_value = mock_response

    tweets = await search_twitter_subnet_mentions(
        18,
        start_date=datetime.date(2024, 4, 1),
        end_date=datetime.date(2024, 4, 2),
    )

    assert isinstance(tweets, list)
    assert tweets[0]["text"] == "Subnet is booming!"
