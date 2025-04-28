import datetime
from unittest.mock import patch, Mock

import pytest

from app.services.datura import search_twitter_subnet_mentions


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_search_twitter_subnet_mentions(mock_get, mocker):
    """Test that search_twitter_subnet_mentions returns expected tweets."""

    # Mock response to return a resolved list of tweets (not a coroutine)
    mock_response = Mock()
    mock_response.json.return_value = [{"text": "Subnet is booming!"}]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call the function you are testing
    tweets = await search_twitter_subnet_mentions(
        netuid=18,
        start_date=datetime.date(2024, 4, 1),
        end_date=datetime.date(2024, 4, 2),
    )

    # Assertions
    assert isinstance(tweets, list)
    assert len(tweets) > 0  # Make sure there are tweets in the list
    assert tweets[0]["text"] == "Subnet is booming!"
