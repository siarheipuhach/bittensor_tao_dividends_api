import asyncio
import logging
from datetime import date, timedelta

from celery import shared_task

from app.services.bittensor import submit_stake_adjustment
from app.services.chutes import query_chutes_sentiment
from app.services.datura import search_twitter_subnet_mentions

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.bittensor.perform_trade_task")
def perform_trade_task(netuid: int, hotkey: str) -> None:
    """
    Celery task to perform sentiment analysis and submit staking/unstaking
    transactions based on Twitter subnet mentions.

    Args:
        netuid (int): The network UID (subnet).
        hotkey (str): The hotkey SS58 address associated with the user/node.
    """

    async def async_trade():
        today = date.today()
        yesterday = today - timedelta(days=1)

        try:
            logger.info(
                f"Fetching tweets for {netuid=} between {yesterday} and {today}."
            )
            tweets = await search_twitter_subnet_mentions(netuid, yesterday, today)
            tweet_texts = [
                tweet.get("text", "") for tweet in tweets if tweet.get("text")
            ]

            if not tweet_texts:
                logger.warning(
                    f"No tweets found for {netuid=}. Skipping stake adjustment."
                )
                return

            logger.info(f"Analyzing sentiment for {len(tweet_texts)} tweets.")
            sentiment_score = await query_chutes_sentiment(tweet_texts)

            logger.info(
                f"Sentiment score: {sentiment_score}. Submitting stake/unstake for hotkey {hotkey}."
            )
            await submit_stake_adjustment(netuid, hotkey, sentiment_score)

        except Exception as e:
            logger.error(
                f"Failed to perform trade task for netuid={netuid}, hotkey={hotkey}: {str(e)}",
                exc_info=True,
            )

    asyncio.run(async_trade())
