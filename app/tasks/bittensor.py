import asyncio
from datetime import date, timedelta

from celery import shared_task

from app.services.bittensor import submit_stake_adjustment
from app.services.chutes import query_chutes_sentiment
from app.services.datura import search_twitter_subnet_mentions


@shared_task
def perform_trade_task(netuid: int, hotkey: str):
    async def async_trade():
        today = date.today()
        yesterday = today - timedelta(days=1)

        tweets = await search_twitter_subnet_mentions(netuid, yesterday, today)
        tweet_texts = [tweet["text"] for tweet in tweets]

        sentiment_score = await query_chutes_sentiment(tweet_texts)
        await submit_stake_adjustment(netuid, hotkey, sentiment_score)

    return asyncio.run(async_trade())
