import asyncio
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from typing import Annotated, Optional, Union
from app.api.v1.schemas import TaoDividendResponse
from app.auth.auth import verify_token
from app.services.bittensor import get_dividends
from app.tasks.bittensor import perform_trade_task

router = APIRouter()


@router.get(
    "/tao_dividends",
    response_model=list[TaoDividendResponse],
)
async def tao_dividends(
    netuid: Optional[int] = Query(default=None),
    hotkey: Optional[str] = Query(default=None),
    trade: bool = Query(default=False),
    _: None = Depends(verify_token),
):
    results: list[TaoDividendResponse] = await get_dividends(netuid, hotkey, trade)

    if trade:
        perform_trade_task.delay(netuid, hotkey)
    return results
