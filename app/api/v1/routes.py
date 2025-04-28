from typing import Optional

from fastapi import APIRouter, Depends, Query, status, BackgroundTasks

from app.api.v1.schemas import TaoDividendResponse
from app.auth.auth import verify_token
from app.services.bittensor import get_dividends
from app.tasks.bittensor import perform_trade_task

router = APIRouter()


@router.get(
    "/tao_dividends",
    response_model=list[TaoDividendResponse],
    status_code=status.HTTP_200_OK,
    summary="Fetch Tao Dividends",
    description=(
        "Fetch Tao Dividends for a given netuid and hotkey. "
        "Optionally trigger sentiment-based stake/unstake if trade is enabled."
    ),
)
async def tao_dividends(
    background_tasks: BackgroundTasks,
    netuid: Optional[int] = Query(
        default=None, description="Subnet netuid ID (optional)"
    ),
    hotkey: Optional[str] = Query(
        default=None, description="Hotkey SS58 address (optional)"
    ),
    trade: bool = Query(
        default=False, description="Whether to perform stake/unstake based on sentiment"
    ),
    _: None = Depends(verify_token),
) -> list[TaoDividendResponse]:
    """
    Fetch Tao dividends from the Bittensor blockchain. Optionally triggers sentiment analysis
    and automated stake/unstake via background task if `trade=true`.
    """
    results = await get_dividends(netuid, hotkey, trade)

    if trade:
        background_tasks.add_task(perform_trade_task.delay, netuid, hotkey)

    return results
