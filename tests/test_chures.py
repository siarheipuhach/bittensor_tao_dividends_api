from unittest.mock import AsyncMock

import pytest

from app.config import settings
from app.services.chutes import query_chutes_sentiment


@pytest.mark.asyncio
async def test_query_chutes_sentiment(mock_httpx_client):
    settings.chutes_api_key = "dummy_key"  # <-- ADD THIS LINE ✅

    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Sentiment Score: 55"}}]
    }
    mock_response.raise_for_status.return_value = None

    mock_httpx_client.post.return_value = mock_response

    tweets = ["Subnet activity is increasing!"]
    score = await query_chutes_sentiment(tweets)

    assert score == 55
