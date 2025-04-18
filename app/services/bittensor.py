import asyncio
import json

from async_substrate_interface.async_substrate import AsyncSubstrateInterface
from bittensor import AsyncSubtensor, DynamicInfo, Balance
from bittensor.core.settings import SS58_FORMAT
from scalecodec.utils import ss58

from app.api.v1.schemas import TaoDividendResponse
from app.cache.redis import redis_cache

from bittensor_wallet import Wallet


# Load wallet from name and path
async def get_wallet(hotkey):
    my_wallet = Wallet(
        name="bittensor_test_wallet_",
        path="~/.bittensor_wallet",
        hotkey=hotkey,
    )
    my_wallet.unlock_hotkey()
    return my_wallet


async def process_single_query(
    netuid: int, hotkey: str, trade: bool, substrate=None
) -> TaoDividendResponse:
    cache_key = f"dividends:{netuid}:{hotkey}"
    cached = await redis_cache.get(cache_key)

    if cached:
        return TaoDividendResponse(
            netuid=netuid,
            hotkey=hotkey,
            dividend=json.loads(cached),
            cached=True,
            stake_tx_triggered=False,
        )
    if substrate is None:
        async with AsyncSubstrateInterface(
            url="wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT
        ) as substrate:
            dividend = await get_tao_dividend_for_hotkey(netuid, hotkey, substrate)
    await redis_cache.set(cache_key, json.dumps(dividend))

    # TODO: trigger background stake/unstake task if trade=True

    return TaoDividendResponse(
        netuid=netuid,
        hotkey=hotkey,
        dividend=dividend,
        cached=False,
        stake_tx_triggered=trade,
    )


async def get_tao_dividend_for_hotkey(netuid: int, hotkey: str, substrate) -> int:

    block_hash = await substrate.get_chain_head()
    result = await substrate.query(
        module="SubtensorModule",
        storage_function="TaoDividendsPerSubnet",
        params=[netuid, hotkey],
        block_hash=block_hash,
    )
    return result.value if result else 0


async def get_hotkeys_for_netuid(netuid: int, substrate) -> list[str]:
    head = await substrate.get_chain_head()
    query_result = await substrate.query_map(
        module="SubtensorModule",
        storage_function="TaoDividendsPerSubnet",
        params=[netuid],
        block_hash=head,
    )

    hotkeys: list[str] = []
    async for key, _ in query_result:
        account_id = bytes(key[0])
        hotkey = ss58.ss58_encode(account_id)
        hotkeys.append(hotkey)

    return hotkeys


async def get_all_netuids() -> list[int]:
    async_subtensor = AsyncSubtensor()
    result: list[DynamicInfo] = await async_subtensor.all_subnets()
    return [res.netuid for res in result]


async def get_dividends(
    netuid: int, hotkey: str, trade: bool
) -> list[TaoDividendResponse]:
    results: list[TaoDividendResponse] = []

    if netuid and hotkey:
        result = await process_single_query(netuid, hotkey, trade)
        return [result]

    async with AsyncSubstrateInterface(
        url="wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT
    ) as substrate:

        if netuid and not hotkey:
            hotkeys = await get_hotkeys_for_netuid(netuid, substrate)
            tasks = [process_single_query(netuid, h, trade, substrate) for h in hotkeys]
            results = await asyncio.gather(*tasks)
            return results

        if not netuid:
            netuids = await get_all_netuids()
            for uid in netuids:
                hotkeys = await get_hotkeys_for_netuid(uid, substrate)
                tasks = [
                    process_single_query(uid, h, trade, substrate) for h in hotkeys
                ]
                results.extend(await asyncio.gather(*tasks))

        return results


async def submit_stake_adjustment(netuid: int, hotkey: str, sentiment: int):
    if sentiment == 0:
        print("Neutral sentiment — no action taken.")
        return

    rao = abs(int(sentiment * 0.01 * 1e9))  # Always positive
    if rao <= 0:
        print("Too small amount — skipping staking.")
        return
    amount = Balance.from_rao(rao).set_unit(netuid)

    wallet = await get_wallet(hotkey)
    subtensor = AsyncSubtensor()  # or get a shared one if available

    if sentiment > 0:
        result = await subtensor.add_stake(
            wallet=wallet, netuid=netuid, hotkey_ss58=hotkey, amount=amount
        )
        print(f"Stake result: {result}")
    else:
        result = await subtensor.unstake(
            wallet=wallet, netuid=netuid, hotkey_ss58=hotkey, amount=amount
        )
        print(f"Unstake result: {result}")
