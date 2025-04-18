from datetime import date

import httpx
from typing import List
from app.config import settings

DATURA_API_URL = "https://apis.datura.ai/twitter"


async def search_twitter_subnet_mentions(
    netuid: int, start_date: date, end_date: date, count: int = 10
) -> List[dict]:
    query = f"Bittensor netuid {netuid}"
    date_format = "%Y-%m-%d"
    params = {
        "query": query,
        "blue_verified": False,
        "end_date": end_date.strftime(date_format),
        "is_image": False,
        "is_quote": False,
        "is_video": False,
        "lang": "en",
        "min_likes": 0,
        "min_replies": 0,
        "min_retweets": 0,
        "sort": "Top",
        "start_date": start_date.strftime(date_format),
        "count": count,
    }

    headers = {
        "Authorization": settings.datura_api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(DATURA_API_URL, params=params, headers=headers)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx
        return response.json()
