import asyncio
import json
import logging
from typing import Optional, List

from async_substrate_interface.async_substrate import AsyncSubstrateInterface
from bittensor import AsyncSubtensor
from bittensor.core.settings import SS58_FORMAT
from bittensor.utils.balance import Balance
from bittensor_wallet import Wallet
from scalecodec.utils import ss58

from app.api.v1.schemas import TaoDividendResponse
from app.cache.redis import redis_cache
from app.db.models import async_session
from app.db.service import save_stake_adjustment

logger = logging.getLogger(__name__)


async def get_wallet(hotkey: str) -> Wallet:
    """Get wallet by hotkey."""
    logger.debug(f"Loading wallet for hotkey: {hotkey}")
    wallet = Wallet(
        name="bittensor_test_wallet_",
        path="~/.bittensor_wallet",
        hotkey=hotkey,
    )
    wallet.unlock_hotkey()
    return wallet


# Core blockchain query
async def process_single_query(
    netuid: int,
    hotkey: str,
    trade: bool,
    substrate: Optional[AsyncSubstrateInterface] = None,
) -> TaoDividendResponse:
    """Process query for netuid, hotkey."""
    cache_key = f"dividends:{netuid}:{hotkey}"
    cached = await redis_cache.get(cache_key)

    if cached:
        logger.info(f"Cache hit for netuid {netuid}, hotkey {hotkey}")
        return TaoDividendResponse(
            netuid=netuid,
            hotkey=hotkey,
            dividend=json.loads(cached),
            cached=True,
            stake_tx_triggered=False,
        )

    logger.info(
        f"Cache miss for netuid {netuid}, hotkey {hotkey}. Fetching from chain..."
    )
    if substrate is None:
        async with AsyncSubstrateInterface(
            url="wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT
        ) as substrate:
            dividend = await get_tao_dividend_for_hotkey(netuid, hotkey, substrate)
    else:
        dividend = await get_tao_dividend_for_hotkey(netuid, hotkey, substrate)

    await redis_cache.set(cache_key, json.dumps(dividend))

    return TaoDividendResponse(
        netuid=netuid,
        hotkey=hotkey,
        dividend=dividend,
        cached=False,
        stake_tx_triggered=trade,
    )


async def get_tao_dividend_for_hotkey(
    netuid: int, hotkey: str, substrate: AsyncSubstrateInterface
) -> int:
    """Get tao dividend for hotkey."""
    block_hash = await substrate.get_chain_head()
    result = await substrate.query(
        module="SubtensorModule",
        storage_function="TaoDividendsPerSubnet",
        params=[netuid, hotkey],
        block_hash=block_hash,
    )
    return result.value if result else 0


async def get_hotkeys_for_netuid(
    netuid: int, substrate: AsyncSubstrateInterface
) -> List[str]:
    """Get hotkey for netuid."""
    head = await substrate.get_chain_head()
    query_result = await substrate.query_map(
        module="SubtensorModule",
        storage_function="TaoDividendsPerSubnet",
        params=[netuid],
        block_hash=head,
    )

    hotkeys = []
    async for key, _ in query_result:
        account_id = bytes(key[0])
        hotkey = ss58.ss58_encode(account_id)
        hotkeys.append(hotkey)

    logger.info(f"Found {len(hotkeys)} hotkeys for netuid {netuid}")
    return hotkeys


async def get_all_netuids() -> List[int]:
    """Get all netuids."""
    subtensor = AsyncSubtensor()
    results = await subtensor.all_subnets()
    netuids = [res.netuid for res in results]
    logger.info(f"Found netuids: {netuids}")
    return netuids


async def get_dividends(
    netuid: Optional[int], hotkey: Optional[str], trade: bool
) -> List[TaoDividendResponse]:
    """Get dividends for netuid."""
    results: List[TaoDividendResponse] = []

    async with AsyncSubstrateInterface(
        url="wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT
    ) as substrate:

        if netuid and hotkey:
            result = await process_single_query(netuid, hotkey, trade, substrate)
            return [result]

        if netuid:
            hotkeys = await get_hotkeys_for_netuid(netuid, substrate)
            tasks = [process_single_query(netuid, h, trade, substrate) for h in hotkeys]
            results = await asyncio.gather(*tasks)
            return results

        netuids = await get_all_netuids()
        for uid in netuids:
            hotkeys = await get_hotkeys_for_netuid(uid, substrate)
            tasks = [process_single_query(uid, h, trade, substrate) for h in hotkeys]
            results.extend(await asyncio.gather(*tasks))

        return results


# Submit staking adjustment
async def submit_stake_adjustment(netuid: int, hotkey: str, sentiment: int) -> None:
    """
    Submit a stake or unstake extrinsic based on the sentiment score.
    """
    if sentiment == 0:
        logger.info(f"Neutral sentiment (0) for {hotkey}. No stake adjustment.")
        return

    rao_amount = abs(int(sentiment * 0.01 * 1e9))  # Convert to rao (TAO * 1e9)
    if rao_amount <= 0:
        logger.warning(f"Skipping adjustment: Computed rao amount is zero.")
        return

    amount = Balance.from_rao(rao_amount).set_unit(netuid)
    wallet = await get_wallet(hotkey)
    subtensor = AsyncSubtensor()

    try:
        if sentiment > 0:
            logger.info(
                f"Submitting stake: {amount.tao:.6f} TAO for {hotkey} on netuid {netuid}"
            )
            result = await subtensor.add_stake(
                wallet=wallet,
                netuid=netuid,
                hotkey_ss58=hotkey,
                amount=amount,
                wait_for_inclusion=True,
            )
            action_type = "stake"
        else:
            logger.info(
                f"Submitting unstake: {amount.tao:.6f} TAO for {hotkey} on netuid {netuid}"
            )
            stake_info = await subtensor.get_stake_for_hotkey(
                hotkey_ss58=hotkey, netuid=netuid
            )

            if stake_info.tao == 0:
                logger.warning(
                    f"No stake to unstake for hotkey {hotkey} on netuid {netuid}. Skipping."
                )
                return

            unstake_amount = min(amount, stake_info)
            result = await subtensor.unstake(
                wallet=wallet,
                netuid=netuid,
                hotkey_ss58=hotkey,
                amount=unstake_amount,
                wait_for_inclusion=True,
            )
            action_type = "unstake"

        logger.info(f"{action_type.capitalize()} result for {hotkey}: {result}")
        async with async_session() as db:
            await save_stake_adjustment(
                db=db,
                netuid=netuid,
                hotkey=hotkey,
                sentiment_score=sentiment,
                action=action_type,
                amount_tao=amount.tao,
            )

    except Exception as e:
        logger.exception(
            f"Error during stake adjustment for {hotkey} on netuid {netuid}: {str(e)}"
        )
