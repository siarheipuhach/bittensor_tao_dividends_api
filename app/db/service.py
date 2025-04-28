from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StakeAdjustment


async def save_stake_adjustment(
    db: AsyncSession,
    *,
    netuid: int,
    hotkey: str,
    sentiment_score: int,
    action: str,
    amount_tao: float,
) -> StakeAdjustment:
    """
    Persist a stake adjustment record into the database.

    Args:
        db (AsyncSession): The async SQLAlchemy session.
        netuid (int): The subnet ID.
        hotkey (str): The hotkey SS58 address.
        sentiment_score (int): Sentiment score (-100 to 100).
        action (str): Type of action, either 'stake' or 'unstake'.
        amount_tao (float): Amount of Tao tokens involved.

    Returns:
        StakeAdjustment: The saved database record.
    """
    adjustment = StakeAdjustment(
        netuid=netuid,
        hotkey=hotkey,
        sentiment_score=sentiment_score,
        action=action,
        amount_tao=amount_tao,
    )
    db.add(adjustment)
    await db.commit()
    await db.refresh(adjustment)
    return adjustment
