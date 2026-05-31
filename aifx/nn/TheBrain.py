# aifx/nn/TheBrain.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio

from aifx.constants.DBrain import DBrainF as BRAINF
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DFile import DFile as FILE
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMQ import DMQEvent
from aifx.constants.DNetwork import DNetwork as NET
from aifx.db.BrainDb import BrainDb
from aifx.db.DbMgr import DbMgr
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQEvent import MQEvent
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQServer import MQServer


class TheBrain:

    def __init__(
        self,
        log_level=DEF.DEFAULT_LOG_LEVEL,
        log_file=FILE.BRAIN_LOG,
        hostname=NET.BRAIN_HOSTNAME,
        port=NET.BRAIN_PORT,
        hb_port=NET.BRAIN_HB_PORT,
        identity=MODULE.BRAIN,
        pub_port=NET.BRAIN_PUB_PORT,
    ) -> None:

        self._log_level = log_level
        self._log_file = log_file
        self._hostname = hostname
        self._port = port
        self._hb_port = hb_port
        self._identity = identity
        self._pub_port = pub_port

        # Log
        self.log = AiFxLog(client_id=identity, log_file=log_file, log_level=log_level)

        # In memory database
        self.db_mgr = DbMgr(db_type=DBF.CACHE, log_level=log_level, log_file=log_file)
        self.broker_db = BrainDb(
            db_mgr=self.db_mgr, log_level=log_level, log_file=log_file
        )

        # Server methods that are exposed over ZeroMQ
        self._srv_methods = {
            METHOD.START_SIM: self.start_sim,
            METHOD.STATUS: self.status,
        }
        self.mq: MQServer | None = None

        # Background MQ control channel listener
        self._mq_bg_task: asyncio.Task | None = None
        self._mq_events_task: asyncio.Task | None = None

        # Track current state
        self._state = BRAINF.UNINITIALIZED

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

    async def _cancel_task(self, task: asyncio.Task | None, name: str) -> None:
        if task is None or task.done() or task is asyncio.current_task():
            return

        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=MQ.LISTEN_INTERVAL)
        except asyncio.CancelledError:
            pass
        except asyncio.TimeoutError:
            self.log.warning(f"{name} task did not cancel cleanly")
        except Exception as e:
            self.log.warning(f"{name} task exception during shutdown: {e}")

    def ensure_data(self, event: MQMsg):

        self.log.info("Fetching data")

    async def handle_mq_event(self, event: MQEvent) -> None:
        if event.routing_id is None:
            self.log.error(f"MQ event has no routing id: {event.event_type}")
            return
        match event.event_type:
            case DMQEvent.START_SIM:
                self.log.info("Start simulation event received")

            case _:
                self.log.error(f"Unknown MQ event: {event}")

    async def quit(self) -> None:
        if self._state == BRAINF.STOPPED:
            return

        if self.mq is not None:
            await self.mq.quit()

        await self._cancel_task(self._mq_events_task, "MQ events")
        await self._cancel_task(self._mq_bg_task, "MQ control channel")

        self.db_mgr.close()
        self.log.info("AI FX Brain shutdown complete")

    async def start(self) -> None:
        if self._state == BRAINF.RUNNING:
            return

        self.mq = MQServer(
            log_level=self._log_level,
            hostname=self._hostname,
            port=self._port,
            hb_port=self._hb_port,
            identity=self._identity,
            pub_port=self._pub_port,
            srv_methods=self._srv_methods,
            topic_prefix=MQ.TOPIC_PREFIX,
        )

        self._mq_bg_task = asyncio.create_task(self.mq.start(), name=BRAINF.BRAIN_MQ)
        self._mq_events_task = asyncio.create_task(
            self.bg_mq_events(), name=BRAINF.BRAIN_MQ_EVENTS
        )

        try:
            await asyncio.gather(self._mq_bg_task, self._mq_events_task)
        except asyncio.CancelledError:
            await self.quit()
            raise
        finally:
            self._state = BRAINF.STOPPED

    def start_nn_run(self, event: MQMsg):
        self.log.info("Start NN run")

    def start_sim(self, event: MQMsg):
        self.log.info("Start simulation run...")
        self.ensure_data(event)
        self.start_nn_run(event)
        self.log.info("End simulation run...")

    def status(self, event: MQMsg):
        self.log.debug("Ready")


def main():
    broker = TheBrain()
    try:
        asyncio.run(broker.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
