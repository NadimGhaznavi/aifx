# aifx/broker/aifx_broker.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from aifx.constants.DAiFx import DAiFx as AIFX
from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DCandle import DCandleF as CANDLEF
from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DFile import DFile as FILE
from aifx.constants.DFrequency import DFrequency as FREQ
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMQ import DMQEvent
from aifx.constants.DNetwork import DNetwork as NET
from aifx.db.BrokerDb import BrokerDb
from aifx.db.DbMgr import DbMgr
from aifx.mgr.OandaMgr import OandaMgr
from aifx.utils.AiFxLog import AiFxLog
from aifx.utils.Feed import Feed
from aifx.zmq.MQEvent import MQEvent
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQServer import MQServer

MsgHandler = Callable[[MQMsg], Any | Awaitable[Any]]

BROKER_LOG = FILE.BROKER_LOG


class Broker:

    def __init__(
        self,
        log_level=DEF.DEFAULT_LOG_LEVEL,
        log_file=FILE.BROKER_LOG,
        hostname=NET.BROKER_HOSTNAME,
        port=NET.BROKER_PORT,
        hb_port=NET.BROKER_HB_PORT,
        identity=MODULE.BROKER,
    ) -> None:

        self._log_level = log_level
        self._log_file = log_file
        self._hostname = hostname
        self._port = port
        self._hb_port = hb_port
        self._identity = identity

        # Log
        self.log = AiFxLog(client_id=identity, log_file=log_file, log_level=log_level)

        # In memory database
        self.db_mgr = DbMgr(db_type=DBF.CACHE, log_level=log_level, log_file=log_file)
        self.broker_db = BrokerDb(
            db_mgr=self.db_mgr, log_level=log_level, log_file=log_file
        )

        # Oanda connections and data exchange
        self.oanda = OandaMgr(log_level=log_level, log_file=log_file)

        # Server methods that are exposed via MQ
        self._srv_methods = {
            METHOD.GET_INSTRUMENTS: self.get_instruments,
            METHOD.GET_RECENT_CANDLES: self.get_recent_candles,
            METHOD.START_FEED: self.start_feed,
        }
        self.mq: MQServer | None = None

        # Track OANDA and ZeroMQ feeds
        self._feeds: dict[str, Feed] = {}

        self.log.info("Initialized")

    async def bg_feed_instrument(self, feed: Feed) -> None:
        self.log.info(f"OANDA feed started: {feed.name}")

        # We're pulling 5 second candlestick data
        # The FEED_INTERVAL is 5 seconds
        # Set the count to 10 to ensure we get all the data
        count = MQ.FEED_INTERVAL * 2

        last_row_count = None

        try:
            while True:
                candles = self.oanda.get_candles(
                    pair_name=feed.name, count=count, granularity=CANDLE.GRAN_S5
                )

                if candles is None:
                    self.log.warning(f"Failed to fetch candles: {feed.name}")
                    await asyncio.sleep(MQ.FEED_INTERVAL)
                    continue

                candles = sorted(
                    candles,
                    key=lambda c: (c.y, c.mo, c.d, c.h, c.mi, c.s),
                )
                self.db_mgr.upsert(
                    table=TABLE.CANDLES,
                    records=[candle.to_dict() for candle in candles],
                    key_fields=[
                        C_CAND.INSTRUMENT,
                        C_CAND.GRANULARITY,
                        C_CAND.Y,
                        C_CAND.MO,
                        C_CAND.D,
                        C_CAND.H,
                        C_CAND.MI,
                        C_CAND.S,
                    ],
                )
                num_rows = self.db_mgr.num_rows(table=TABLE.CANDLES)
                if num_rows != last_row_count:
                    last_row_count = num_rows
                    self.log.debug(f"Candles table row count: {num_rows}")
                await asyncio.sleep(MQ.FEED_INTERVAL)

        except asyncio.CancelledError:
            self.log.info(f"OANDA feed loop stopped: {feed.name}")
            raise

        except Exception as e:
            self.log.critical(f"Background feed exception: {e}")

    async def bg_mq_events(self) -> None:
        assert self.mq is not None

        try:
            while True:
                event = await self.mq.event_queue.get()

                try:
                    await self.handle_mq_event(event)
                finally:
                    self.mq.event_queue.task_done()

        except asyncio.CancelledError:
            raise

    async def bg_publish_instrument(self, feed: Feed) -> None:
        self.log.info(f"Starting MQ feed: {feed.name}")

        assert self.mq is not None

        topic = self.mq.topic(f"candles.{feed.name}")

        try:
            while True:
                candles = self.broker_db.get_recent_candles(feed.name, limit=10)

                for candle in candles:
                    if (
                        feed.last_published_key is None
                        or candle.candle_key > feed.last_published_key
                    ):
                        await self.mq.publish(topic=topic, payload=candle.to_dict())
                        feed.last_published_key = candle.candle_key
                        self.log.debug(f"Published: {candle}")

                await asyncio.sleep(MQ.FEED_INTERVAL)

        except asyncio.CancelledError:
            self.log.info(f"MQ feed stopped: {feed.name}")
            raise

        except Exception as e:
            self.log.critical(
                f"MQ feed crashed for {feed.name}: {type(e).__name__}: {e}"
            )
            raise

    async def get_candles_oanda(self, instrument, count):
        return await asyncio.to_thread(
            self.oanda.get_candles(
                pair_name=instrument, count=count, granularity=FREQ.S5
            )
        )

    async def get_instruments_oanda(self):
        return await asyncio.to_thread(self.oanda.get_instruments)

    async def get_instruments(self, _msg: MQMsg):

        self.log.debug("Request: Instruments")

        instruments = self.broker_db.get_instruments()

        if not instruments:
            instruments = await self.get_instruments_oanda()

            if instruments:
                instruments = sorted(instruments, key=lambda ins: ins.name)
                self.db_mgr.upsert(
                    table=TABLE.INSTRUMENTS,
                    records=[ins.to_dict() for ins in instruments],
                    key_fields=[INS.NAME],
                )

        if instruments:
            return {INSF.INSTRUMENTS: [ins.to_dict() for ins in instruments]}

        return {}

    async def get_recent_candles(self, msg: MQMsg):
        self.log.debug("Request: Recent candles")

        candles = self.broker_db.get_recent_candles(
            name=msg.payload[C_CAND.INSTRUMENT], limit=msg.payload[DBF.LIMIT]
        )

        instrument = msg.payload[INSF.INSTRUMENT]
        count = msg.payload[DBF.LIMIT]

        if not candles:
            candles = await self.get_candles_oanda(instrument=instrument, count=count)

            if candles:
                self.db_mgr.upsert(
                    table=TABLE.CANDLES,
                    records=[candle.to_dict() for candle in candles],
                    key_fields=[
                        C_CAND.Y,
                        C_CAND.MO,
                        C_CAND.D,
                        C_CAND.H,
                        C_CAND.MI,
                        C_CAND.S,
                    ],
                )

        if candles:
            return {CANDLEF.CANDLES: [candle.to_dict() for candle in candles]}

        return {CANDLEF.CANDLES: []}

    async def handle_mq_event(self, event: MQEvent) -> None:
        if event.routing_id is None:
            self.log.error(f"MQ event has no routing id: {event.event_type}")
            return
        client_id = event.routing_id.decode(AIFX.UTF_8)
        match event.event_type:
            case DMQEvent.CLIENT_ADDED:
                self.log.info(f"Client added: {client_id}")

            case DMQEvent.CLIENT_REMOVED:
                self.log.info(f"Client removed: {client_id}")
                # later:
                # self.remove_client_subscriptions(event.routing_id)
                # self.stop_unused_pubsub_streams()

            case _:
                self.log.warning(f"Unknown MQ event: {event}")

    async def start(self) -> None:
        self.mq = MQServer(
            log_level=self._log_level,
            hostname=self._hostname,
            port=self._port,
            hb_port=self._hb_port,
            identity=self._identity,
            srv_methods=self._srv_methods,
            topic_prefix=MQ.TOPIC_PREFIX,
        )

        await asyncio.gather(
            self.mq.start(),
            self.bg_mq_events(),
        )

    async def start_feed(self, msg: MQMsg):
        instrument = msg.payload

        feeds = self._feeds

        feed = Feed(name=instrument[C_INST.NAME])

        if feed.name in feeds:
            self.log.info(f"Feed already started: {feed.name}")
            return {
                C_INST.NAME: feed.name,
                INS.STARTED: True,
            }

        self.log.info(f"New feed request: {feed.name}")
        feeds[feed.name] = feed

        # Loop: Feed OANDA data into the DB
        feed.oanda_task = asyncio.create_task(
            self.bg_feed_instrument(feed=feed), name=f"feed-{feed.name}"
        )
        feed.oanda_running = True

        # Loop: Publish DB data on a PUB socket
        feed.pub_task = asyncio.create_task(
            self.bg_publish_instrument(feed=feed), name=f"pub-{feed.name}"
        )
        feed.pub_running = True

        return {
            C_INST.NAME: feed.name,
            INS.STARTED: True,
        }


def main():
    broker = Broker(
        log_file=BROKER_LOG,
        log_level=DEF.DEFAULT_LOG_LEVEL,
    )
    asyncio.run(broker.start())


if __name__ == "__main__":
    main()
