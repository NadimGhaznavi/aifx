# aifx/db/DbServer.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
import os
from pathlib import Path
from typing import Any

from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DDir import DDir as DIR
from aifx.constants.DFile import DFile as FILE
from aifx.constants.DLogging import DAiFxLog as LOG
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DNetwork import DNetwork as NET

from aifx.db.DbMgr import DbMgr
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQServer import MQServer

DEFAULT_DB_LOG_LEVEL = LOG.INFO


class DbServer:

    def __init__(
        self,
        log_level=DEFAULT_DB_LOG_LEVEL,
        log_file=FILE.DB_SERVER_LOG,
        hostname=NET.DB_SERVER_HOSTNAME,
        port=NET.DB_PORT,
        hb_port=NET.DB_HB_PORT,
        identity=MODULE.DB_SERVER,
        db_file: str | None = None,
    ) -> None:
        self._log_level = log_level
        self._log_file = log_file
        self._hostname = hostname
        self._port = port
        self._hb_port = hb_port
        self._identity = identity

        # Log
        self.log = AiFxLog(client_id=identity, log_file=log_file, log_level=log_level)

        if db_file is None:
            # File based database ...
            aifx_dir = os.path.join(Path.home(), DIR.AIFX_DIR)
            if not os.path.exists(aifx_dir):
                try:
                    os.makedirs(aifx_dir)
                except Exception as e:
                    raise PermissionError(f"ERROR: {e}")
            # Database storage file
            self._db_file = os.path.join(aifx_dir, FILE.DB_SERVER_STORAGE_FILE)
        else:
            self._db_file = db_file

        # Use the DbMgr class to handle the sqlite specifics
        self.db = DbMgr(
            db_type=DBF.FILE,
            log_level=self._log_level,
            log_file=self._log_file,
            db_file=self._db_file,
        )

        # Server methods that are exposed over ZeroMQ
        self._srv_methods = {
            METHOD.NUM_ROWS: self.num_rows,
            METHOD.SELECT_ALL: self.select_all,
            METHOD.SELECT_ONE: self.select_one,
            METHOD.UPSERT: self.upsert,
        }

        # We'll setup the ZeroMQ Server in start()
        self.mq: MQServer | None = None
        self._mq_bg_task: asyncio.Task | None = None
        self._mq_msgs_task: asyncio.Task | None = None

    # ----- Db Ops exposed over MQ -----

    @staticmethod
    def _rows_to_dicts(rows) -> list[dict[str, Any]]:
        return [dict(row) for row in rows]

    def num_rows(self, event: MQMsg) -> dict[str, int]:
        self.log.debug("num_rows()")
        return {"rows": self.db.num_rows(table=event.payload["table"])}

    def select_all(self, event: MQMsg) -> dict[str, list[dict[str, Any]]]:
        self.log.debug("select_all()")
        rows = self.db.select_all(
            table=event.payload["table"],
            where=event.payload.get("where"),
            params=tuple(event.payload.get("params") or ()),
            order_by=event.payload.get("order_by"),
            limit=event.payload.get("limit"),
        )
        return {"records": self._rows_to_dicts(rows)}

    def select_one(self, event: MQMsg) -> dict[str, dict[str, Any] | None]:
        self.log.debug("select_one()")
        row = self.db.select_one(
            table=event.payload["table"],
            where=event.payload.get("where"),
            params=tuple(event.payload.get("params") or ()),
            order_by=event.payload.get("order_by"),
        )
        return {"record": None if row is None else dict(row)}

    def upsert(self, event: MQMsg) -> dict[str, int]:
        table = event.payload["table"]
        records = event.payload["records"]
        key_fields = event.payload["key_fields"]
        self.log.debug(f"upsert({table} : {records}")
        rows = self.db.upsert(
            table=table,
            records=records,
            key_fields=key_fields,
        )
        return {"rows": rows}

    # ----- End of Db Ops -----

    async def handle_mq_msg(self, event) -> None:
        self.log.debug(f"MQ event: {event}")

    async def bg_mq_msgs(self) -> None:
        assert self.mq is not None

        try:
            while True:
                event = await self.mq.event_queue.get()

                try:
                    await self.handle_mq_msg(event)
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

    async def quit(self) -> None:
        if self.mq is not None:
            await self.mq.quit()

        await self._cancel_task(self._mq_msgs_task, "MQ events")
        await self._cancel_task(self._mq_bg_task, "MQ control channel")

        self.db.close()
        self.log.info("AI FX DB Server shutdown complete")

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

        self._mq_bg_task = asyncio.create_task(self.mq.start(), name=DBF.SERVER_MQ)
        self._mq_msgs_task = asyncio.create_task(
            self.bg_mq_msgs(), name=DBF.SERVER_MQ_MSGS
        )

        try:
            await asyncio.gather(self._mq_bg_task, self._mq_msgs_task)
        except asyncio.CancelledError:
            await self.quit()
            raise


def main():
    db_server = DbServer()
    try:
        asyncio.run(db_server.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
