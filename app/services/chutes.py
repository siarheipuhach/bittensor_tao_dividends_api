import json
import re
from typing import List

import aiohttp

from app.config import settings


def extract_sentiment_score(text: str) -> int:
    """
    Extracts sentiment score from structured Chutes LLM response.
    Expects a line like "**Sentiment Score: 40**" in the response.
    """
    try:
        # Look for "Sentiment Score: <number>" pattern
        match = re.search(r"Sentiment Score[:\s]*(-?\d+)", text)
        if match:
            score = int(match.group(1))
            return max(-100, min(100, score))
    except Exception as e:
        print(f"Failed to extract sentiment score: {e}")

    return 0  # Fallback


async def query_chutes_sentiment(tweets: List[str]) -> int:
    """
    Sends tweets to Chutes.ai using a LLaMA LLM to calculate sentiment score (-100 to 100).
    """
    prompt = (
        "Analyze the sentiment of the following tweets about a subnet in the Bittensor network. "
        "Return a single integer sentiment score between -100 and 100. "
        "Only include the score in your final answer like: 'Sentiment Score: 25'\n\n"
        + "\n\n".join(tweets)
    )

    headers = {
        "Authorization": f"Bearer {settings.chutes_api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "chutesai/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://llm.chutes.ai/v1/chat/completions", headers=headers, json=body
        ) as response:
            data = await response.json()
    try:
        content = data["choices"][0]["message"]["content"]
        return extract_sentiment_score(content)
    except Exception as e:
        print(f"Error parsing sentiment: {e}")
        return 0
