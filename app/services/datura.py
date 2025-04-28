from datetime import date
from typing import List

import httpx
import logging

from app.config import settings

logger = logging.getLogger(__name__)

DATURA_API_URL = "https://apis.datura.ai/twitter"


async def search_twitter_subnet_mentions(
    netuid: int,
    start_date: date,
    end_date: date,
    count: int = 10,
) -> List[dict]:
    """
    Queries recent tweets mentioning a specific Bittensor subnet from Datura.ai.

    Args:
        netuid (int): The subnet ID to search mentions for.
        start_date (date): The start date for the query.
        end_date (date): The end date for the query.
        count (int, optional): Number of tweets to retrieve. Defaults to 10.

    Returns:
        List[dict]: A list of tweet objects from the Datura.ai API.
    """
    query = f"Bittensor netuid {netuid}"
    date_format = "%Y-%m-%d"

    params = {
        "query": query,
        "blue_verified": False,
        "start_date": start_date.strftime(date_format),
        "end_date": end_date.strftime(date_format),
        "is_image": False,
        "is_quote": False,
        "is_video": False,
        "lang": "en",
        "min_likes": 0,
        "min_replies": 0,
        "min_retweets": 0,
        "sort": "Top",
        "count": count,
    }

    headers = {
        "Authorization": settings.datura_api_key,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(DATURA_API_URL, params=params, headers=headers)
            response.raise_for_status()
            tweets = await response.json()
            logger.info(f"Retrieved {len(tweets)} tweets for netuid {netuid}.")
            return tweets

    except httpx.HTTPStatusError as http_err:
        logger.error(
            f"Datura API HTTP error: {http_err.response.status_code} {http_err.response.text}"
        )
        return []

    except Exception as e:
        logger.error(f"Unexpected error when querying Datura API: {e}", exc_info=True)
        return []
