# tests/unit/test_feed.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio

from aifx.utils.Feed import Feed


def test_feed_stores_name_and_defaults_runtime_state() -> None:
    feed = Feed(name="USD_CAD")

    assert feed.name == "USD_CAD"
    assert feed.oanda_task is None
    assert feed.oanda_running is False
    assert feed.pub_task is None
    assert feed.pub_running is False
    assert feed.last_published_key is None


def test_feed_runtime_state_can_be_updated() -> None:
    async def wait_forever() -> None:
        await asyncio.Event().wait()

    async def run() -> None:
        feed = Feed(name="USD_CAD")
        oanda_task = asyncio.create_task(wait_forever())
        pub_task = asyncio.create_task(wait_forever())
        try:
            feed.oanda_task = oanda_task
            feed.oanda_running = True
            feed.pub_task = pub_task
            feed.pub_running = True
            feed.last_published_key = "20260514193005"

            assert feed.oanda_task is oanda_task
            assert feed.oanda_running is True
            assert feed.pub_task is pub_task
            assert feed.pub_running is True
            assert feed.last_published_key == "20260514193005"
        finally:
            oanda_task.cancel()
            pub_task.cancel()
            await asyncio.gather(oanda_task, pub_task, return_exceptions=True)

    asyncio.run(run())


def test_feed_supports_dataclass_equality_for_same_state() -> None:
    first = Feed(name="USD_CAD", last_published_key="20260514193005")
    second = Feed(name="USD_CAD", last_published_key="20260514193005")

    assert first == second
