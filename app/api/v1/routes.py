import asyncio

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from typing import Annotated, Optional, Union
from app.api.v1.schemas import TaoDividendResponse
from app.auth.auth import verify_token
from app.services.bittensor import (
    get_tao_dividend_for_hotkey,
    get_all_netuids,
    get_hotkeys_for_netuid,
    get_dividends,
)
from app.cache.redis import redis_cache
import json

router = APIRouter()


# @router.get("/tao_dividends", response_model=list[TaoDividendResponse])
# async def tao_dividends(
#     authorization: Annotated[str, Depends(verify_token)],
#     netuid: Annotated[Optional[int], Query()] = None,
#     hotkey: Annotated[Optional[str], Query()] = None,
#     trade: Annotated[
#             bool,
#             Query(description="Whether to trigger stake/unstake tx")
#         ] = False
# ) -> list[TaoDividendResponse]:
#     results: list[TaoDividendResponse] = []
#
#     if netuid is None:
#         netuids = await get_all_netuids()
#         for n in netuids:
#             hotkeys = await get_hotkeys_for_netuid(n)
#             for h in hotkeys:
#                 res = await process_single_query(n, h, trade)
#                 results.append(res)
#     elif hotkey is None:
#         # netuid given, but not hotkey → return all hotkeys for that netuid
#         hotkeys = await get_hotkeys_for_netuid(netuid)
#         results = await asyncio.gather(*[
#             process_single_query(netuid, h, trade) for h in hotkeys
#         ])
#     else:
#         # both netuid and hotkey provided
#         res = await process_single_query(netuid, hotkey, trade)
#         results.append(res)
#
#     return results


@router.get(
    "/tao_dividends",
    response_model=Union[TaoDividendResponse, list[TaoDividendResponse]],
)
async def tao_dividends(
    netuid: Optional[int] = Query(default=None),
    hotkey: Optional[str] = Query(default=None),
    trade: bool = Query(default=False),
    _: None = Depends(verify_token),
):
    results: list[TaoDividendResponse] = await get_dividends(netuid, hotkey, trade)
    return results
