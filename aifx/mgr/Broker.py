# aifx/broker/aifx_broker.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Any
from collections.abc import Callable, Awaitable
import asyncio

from aifx.constants.DAiFx import DAiFx as AIFX
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DDb import DDbF as DBF, DTable as TABLE, DColInstrument as COL
from aifx.constants.DFile import DFile as FILE
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DMQ import DMQ as MQ, DMQEvent


from aifx.utils.AiFxLog import AiFxLog
from aifx.db.DbMgr import DbMgr
from aifx.db.BrokerDb import BrokerDb
from aifx.forex.Instrument import Instrument
from aifx.mgr.OandaMgr import OandaMgr
from aifx.zmq.MQServer import MQServer
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQEvent import MQEvent

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
    ):

        self._log_level = log_level
        self._log_file = log_file
        self._hostname = hostname
        self._port = port
        self._hb_port = hb_port
        self._identity = identity

        # Log
        self.log = AiFxLog(client_id=identity, log_file=log_file, log_level=log_level)

        # In memory database
        self.db_mgr = DbMgr(DBF.CACHE, logfile=log_file)
        self.broker_db = BrokerDb(db_mgr=self.db_mgr)

        # Oanda connections and data exchange
        self.oanda = OandaMgr()

        # Server methods that are exposed via MQ
        self._srv_methods = {
            METHOD.GET_INSTRUMENTS: self.get_instruments,
            METHOD.START_FEED: self.start_feed,
        }
        self.mq: MQServer | None = None

        self.log.info("Initialized")

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

    async def get_instruments_oanda(self):
        return await asyncio.to_thread(self.oanda.get_instruments)

    async def get_instruments(self, _msg: MQMsg):

        self.log.debug("get_instruments()")

        instruments = self.broker_db.get_instruments()

        if not instruments:
            instruments = await self.get_instruments_oanda()

        if instruments:
            instruments = sorted(instruments, key=lambda ins: ins.name)

            cur_pub_port = NET.BROKER_PUB_PORTS_START

            for ins in instruments:
                ins.pub_port = cur_pub_port
                cur_pub_port += 1

            self.db_mgr.upsert(
                table=TABLE.INSTRUMENTS,
                records=[ins.to_dict() for ins in instruments],
                key_fields=[INS.NAME],
            )
        return {INS.INSTRUMENTS: [ins.to_dict() for ins in instruments]}

    async def handle_mq_event(self, event: MQEvent) -> None:
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

        name = instrument[COL.NAME]
        pub_port = instrument[COL.PUB_PORT]

        self.log.info(f"START_FEED received: {name}, pub_port={pub_port}")

        return {
            COL.NAME: name,
            COL.PUB_PORT: pub_port,
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
