# aifx/zmq/MQDbClient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
from collections.abc import Callable
from typing import Any

import zmq
import zmq.asyncio

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DNetwork import DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQUtils import MQUtils

SubHandler = Callable[[str, dict], Any]


class MQDbClient:
    def __init__(
        self,
        log_level: str = DEF.DEFAULT_LOG_LEVEL,
        server_hostname: str = NET.DB_SERVER_HOSTNAME,
        server_port: int = NET.DB_PORT,
        identity: str = MODULE.MQ_DB_CLIENT,
    ) -> None:
        self.log = AiFxLog(client_id=identity, log_level=log_level)

        self._server_hostname = server_hostname
        self._server_port = server_port
        self._identity = identity
        self._address = f"{NETF.TCP}{server_hostname}:{server_port}"

        self._ctx = zmq.asyncio.Context()
        self._socket = self._ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity.encode())

        self._started = False
        self._stopped = False

    async def num_rows(self, payload: dict) -> dict:
        return await self.request(method=METHOD.NUM_ROWS, payload=payload)

    async def select_all(self, payload: dict) -> dict:
        return await self.request(method=METHOD.SELECT_ALL, payload=payload)

    async def select_one(self, payload: dict) -> dict:
        return await self.request(method=METHOD.SELECT_ONE, payload=payload)

    async def upsert(self, payload: dict) -> dict:
        return await self.request(method=METHOD.UPSERT, payload=payload)

    async def request(self, method: str, payload: dict | None = None) -> dict:
        msg = MQMsg(
            sender=self._identity,
            target=MODULE.DB_SERVER,
            method=method,
            payload=payload or {},
        )

        await self._socket.send(msg.to_json())
        reply_data = await asyncio.wait_for(
            self._socket.recv(copy=True), timeout=OANDA.TIMEOUT
        )
        reply = MQMsg.from_json(MQUtils.ensure_bytes(reply_data))
        return reply.payload

    async def quit(self) -> None:
        if self._stopped:
            return

        self._stopped = True
        self._started = False

        MQUtils.ignore_zmq_teardown(
            lambda: self._socket.disconnect(self._address),
            f"socket.disconnect({self._address})",
        )
        MQUtils.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.close(linger=0)",
        )
        MQUtils.ignore_zmq_teardown(
            lambda: self._ctx.destroy(linger=0),
            "ctx.destroy(linger=0)",
        )

    async def start(self) -> None:
        if self._started:
            return

        self._socket.connect(self._address)
        self._started = True
        self._stopped = False
