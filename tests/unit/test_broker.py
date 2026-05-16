# tests/unit/test_broker.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
from unittest.mock import AsyncMock, MagicMock

from aifx.constants.DCandle import DCandleF as CANDLEF
from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.mgr.Broker import Broker
from aifx.zmq.MQMsg import MQMsg


def _broker() -> Broker:
    return Broker(log_file=None)


def _recent_candles_msg(instrument: str = "USD_CAD", limit: int = 10) -> MQMsg:
    return MQMsg(
        sender="client",
        target="broker",
        method=METHOD.GET_RECENT_CANDLES,
        payload={
            C_CAND.INSTRUMENT: instrument,
            DBF.LIMIT: limit,
        },
    )


def test_get_instruments_returns_cached_db_instruments(sample_instrument) -> None:
    async def run() -> None:
        broker = _broker()
        broker.broker_db.get_instruments = MagicMock(return_value=[sample_instrument])
        broker.get_instruments_oanda = AsyncMock()

        result = await broker.get_instruments(
            MQMsg(sender="client", target="broker", method=METHOD.GET_INSTRUMENTS)
        )

        assert result == {INSF.INSTRUMENTS: [sample_instrument.to_dict()]}
        broker.get_instruments_oanda.assert_not_awaited()

    asyncio.run(run())


def test_get_instruments_fetches_oanda_when_cache_is_empty(
    sample_instrument,
) -> None:
    async def run() -> None:
        broker = _broker()
        broker.broker_db.get_instruments = MagicMock(return_value=None)
        broker.get_instruments_oanda = AsyncMock(return_value=[sample_instrument])
        broker.db_mgr.upsert = MagicMock(return_value=1)

        result = await broker.get_instruments(
            MQMsg(sender="client", target="broker", method=METHOD.GET_INSTRUMENTS)
        )

        assert result == {INSF.INSTRUMENTS: [sample_instrument.to_dict()]}
        broker.get_instruments_oanda.assert_awaited_once_with()
        broker.db_mgr.upsert.assert_called_once()

    asyncio.run(run())


def test_get_instruments_returns_empty_dict_when_no_data() -> None:
    async def run() -> None:
        broker = _broker()
        broker.broker_db.get_instruments = MagicMock(return_value=None)
        broker.get_instruments_oanda = AsyncMock(return_value=None)
        broker.db_mgr.upsert = MagicMock()

        result = await broker.get_instruments(
            MQMsg(sender="client", target="broker", method=METHOD.GET_INSTRUMENTS)
        )

        assert result == {}
        broker.db_mgr.upsert.assert_not_called()

    asyncio.run(run())


def test_get_recent_candles_returns_cached_db_candles(sample_candle) -> None:
    async def run() -> None:
        broker = _broker()
        broker.broker_db.get_recent_candles = MagicMock(return_value=[sample_candle])
        broker.get_candles_oanda = AsyncMock()

        result = await broker.get_recent_candles(_recent_candles_msg())

        assert result == {CANDLEF.CANDLES: [sample_candle.to_dict()]}
        broker.get_candles_oanda.assert_not_awaited()

    asyncio.run(run())


def test_get_recent_candles_fetches_oanda_when_cache_is_empty(
    sample_candle,
) -> None:
    async def run() -> None:
        broker = _broker()
        broker.broker_db.get_recent_candles = MagicMock(return_value=[])
        broker.get_candles_oanda = AsyncMock(return_value=[sample_candle])
        broker.db_mgr.upsert = MagicMock(return_value=1)

        result = await broker.get_recent_candles(_recent_candles_msg(limit=5))

        assert result == {CANDLEF.CANDLES: [sample_candle.to_dict()]}
        broker.get_candles_oanda.assert_awaited_once_with(
            instrument="USD_CAD",
            count=5,
        )
        broker.db_mgr.upsert.assert_called_once()

    asyncio.run(run())


def test_get_recent_candles_returns_empty_list_when_no_data() -> None:
    async def run() -> None:
        broker = _broker()
        broker.broker_db.get_recent_candles = MagicMock(return_value=[])
        broker.get_candles_oanda = AsyncMock(return_value=None)
        broker.db_mgr.upsert = MagicMock()

        result = await broker.get_recent_candles(_recent_candles_msg())

        assert result == {CANDLEF.CANDLES: []}
        broker.db_mgr.upsert.assert_not_called()

    asyncio.run(run())


def test_start_feed_creates_feed_and_background_tasks() -> None:
    async def wait_until_cancelled(feed):
        await asyncio.Event().wait()

    async def run() -> None:
        broker = _broker()
        broker.bg_feed_instrument = wait_until_cancelled
        broker.bg_publish_instrument = wait_until_cancelled

        result = await broker.start_feed(
            MQMsg(
                sender="client",
                target="broker",
                method=METHOD.START_FEED,
                payload={C_INST.NAME: "USD_CAD"},
            )
        )

        feed = broker._feeds["USD_CAD"]
        try:
            assert result == {C_INST.NAME: "USD_CAD", INS.STARTED: True}
            assert feed.name == "USD_CAD"
            assert feed.oanda_running is True
            assert feed.pub_running is True
            assert feed.oanda_task is not None
            assert feed.pub_task is not None
        finally:
            assert feed.oanda_task is not None
            assert feed.pub_task is not None
            feed.oanda_task.cancel()
            feed.pub_task.cancel()
            await asyncio.gather(
                feed.oanda_task,
                feed.pub_task,
                return_exceptions=True,
            )

    asyncio.run(run())


def test_start_feed_is_idempotent_for_existing_feed() -> None:
    async def wait_until_cancelled(feed):
        await asyncio.Event().wait()

    async def run() -> None:
        broker = _broker()
        broker.bg_feed_instrument = wait_until_cancelled
        broker.bg_publish_instrument = wait_until_cancelled
        msg = MQMsg(
            sender="client",
            target="broker",
            method=METHOD.START_FEED,
            payload={C_INST.NAME: "USD_CAD"},
        )

        first = await broker.start_feed(msg)
        feed = broker._feeds["USD_CAD"]
        oanda_task = feed.oanda_task
        pub_task = feed.pub_task
        second = await broker.start_feed(msg)

        try:
            assert first == {C_INST.NAME: "USD_CAD", INS.STARTED: True}
            assert second == {C_INST.NAME: "USD_CAD", INS.STARTED: True}
            assert broker._feeds["USD_CAD"] is feed
            assert feed.oanda_task is oanda_task
            assert feed.pub_task is pub_task
        finally:
            assert feed.oanda_task is not None
            assert feed.pub_task is not None
            feed.oanda_task.cancel()
            feed.pub_task.cancel()
            await asyncio.gather(
                feed.oanda_task,
                feed.pub_task,
                return_exceptions=True,
            )

    asyncio.run(run())
