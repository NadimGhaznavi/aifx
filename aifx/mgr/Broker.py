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

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DDb import DDbF as DBF, DTable as TABLE
from aifx.constants.DFile import DFile as FILE
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DMQ import DMQ as MQ


from aifx.utils.AIFxLog import AiFxLog
from aifx.db.DbMgr import DbMgr
from aifx.db.BrokerDb import BrokerDb
from aifx.forex.Instrument import Instrument
from aifx.mgr.OandaMgr import OandaMgr
from aifx.mgr.BrokerBase import BrokerBase
from aifx.zmq.ServerMQ import ServerMQ
from aifx.zmq.MQMsg import MQMsg

MsgHandler = Callable[[MQMsg], Any | Awaitable[Any]]

BROKER_LOG = FILE.BROKER_LOG
LOG_LEVEL = DEF.DEFAULT_LOG_LEVEL


class Broker(BrokerBase):

    def __init__(
        self,
        log_level=DEF.DEFAULT_LOG_LEVEL,
        log_file=FILE.BROKER_LOG,
        address=NET.BROKER_HOSTNAME,
        port=NET.BROKER_PORT,
        hb_port=NET.BROKER_HB_PORT,
        identity=MODULE.BROKER,
    ):

        self._log_level = log_level
        self._log_file = log_file
        self._address = address
        self._port = port
        self._hb_port = hb_port
        self._identity = identity

        self.log = AiFxLog(client_id=identity, log_file=log_file, log_level=log_level)

        self.db_mgr = DbMgr(DBF.CACHE, dblogfile=log_file)
        self.broker_db = BrokerDb(db_mgr=self.db_mgr)
        self.oanda = OandaMgr()

        self._srv_methods = {METHOD.GET_INSTRUMENTS: self.get_instruments}
        self.mq: ServerMQ | None = None

        self.log.info("Initialized")

    async def get_instruments_oanda(self):
        return await asyncio.to_thread(self.oanda.get_instruments)

    async def get_instruments(self, _msg: MQMsg):

        self.log.debug("get_instruments()")
        instruments = self.broker_db.get_instruments()
        if not instruments:
            instruments = await self.get_instruments_oanda()
            if instruments:
                self.db_mgr.update(
                    table=TABLE.INSTRUMENTS,
                    records=[ins.to_dict() for ins in instruments],
                )
        return instruments

    def start(self) -> None:
        self.mq = ServerMQ(
            log_level=self._log_level,
            addr=self._address,
            port=self._port,
            hb_port=self._hb_port,
            identity=self._identity,
            srv_methods=self._srv_methods,
            topic_prefix=MQ.TOPIC_PREFIX,
        )
        self.mq.start()


def main():
    broker = Broker(
        log_file=BROKER_LOG,
        log_level=LOG_LEVEL,
    )
    broker.start()


if __name__ == "__main__":
    main()
