import types

import pytest

from app.services.bittensor import get_hotkeys_for_netuid


@pytest.mark.asyncio
async def test_get_all_netuids(mocker):
    mock_subtensor = mocker.patch(
        "app.services.bittensor.AsyncSubtensor", autospec=True
    )
    fake_instance = mock_subtensor.return_value
    fake_instance.all_subnets.return_value = [
        types.SimpleNamespace(netuid=18),
        types.SimpleNamespace(netuid=19),
    ]

    from app.services.bittensor import get_all_netuids

    netuids = await get_all_netuids()

    assert netuids == [18, 19]


@pytest.mark.asyncio
async def test_get_hotkeys_for_netuid(mocker):
    mock_substrate = mocker.Mock()
    mock_substrate.get_chain_head = mocker.AsyncMock(return_value="fake_block")
    mock_substrate.query_map = mocker.AsyncMock()

    fake_result = [([b"\x00" * 32], {"some": "data"})]  # fake 32-byte key
    mock_substrate.query_map.return_value.__aiter__.return_value = iter(fake_result)

    hotkeys = await get_hotkeys_for_netuid(18, mock_substrate)
    assert isinstance(hotkeys, list)
