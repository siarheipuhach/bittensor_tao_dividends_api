import re
import logging
from typing import List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def extract_sentiment_score(text: str) -> int:
    """
    Extracts the sentiment score from the Chutes.ai LLM structured response.
    Expects a line formatted like '**Sentiment Score: 40**' somewhere in the text.

    Args:
        text (str): The full LLM response text.

    Returns:
        int: Sentiment score between -100 and 100. Returns 0 if parsing fails.
    """
    try:
        match = re.search(r"Sentiment Score[:\s]*(-?\d+)", text)
        if match:
            score = int(match.group(1))
            return max(-100, min(100, score))
    except Exception as e:
        logger.error(f"Failed to extract sentiment score: {e}", exc_info=True)

    return 0


async def query_chutes_sentiment(tweets: List[str]) -> int:
    """
    Sends a batch of tweets to Chutes.ai's LLaMA model to compute overall sentiment.

    Args:
        tweets (List[str]): List of tweet texts to analyze.

    Returns:
        int: Calculated sentiment score in the range [-100, 100].
    """
    prompt = (
        "Analyze the sentiment of the following tweets about a subnet in the Bittensor network. "
        "Return a single integer sentiment score between -100 and 100. "
        "Only include the score in your final answer like: 'Sentiment Score: 25'.\n\n"
        + "\n\n".join(tweets)
    )

    headers = {
        "Authorization": f"Bearer {settings.chutes_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "chutesai/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = await response.json()

        content = data["choices"][0]["message"]["content"]
        sentiment_score = extract_sentiment_score(content)
        logger.info(f"✅ Extracted sentiment score: {sentiment_score}")
        return sentiment_score

    except httpx.HTTPStatusError as http_err:
        logger.error(
            f"HTTP error from Chutes API: {http_err.response.status_code} {http_err.response.text}",
            exc_info=True,
        )
    except Exception as e:
        logger.error(f"Unexpected error querying Chutes sentiment: {e}", exc_info=True)

    return 0
