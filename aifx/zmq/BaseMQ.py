# aifx/zmq/BaseMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Any
from collections.abc import Awaitable, Callable

import time
import asyncio
import zmq
import zmq.asyncio
from zmq.sugar.frame import Frame

from aifx.constants.DAiFx import DAiFx as AIFX
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ, DMQF as MQF
from aifx.constants.DNetwork import DNetwork as NET, DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA

from aifx.zmq.MQMsg import MQMsg

MsgHandler = Callable[[MQMsg], Any | Awaitable[Any]]


class BaseMQ:
    def __init__(
        self,
        router_address: str = NET.BROKER_HOSTNAME,
        router_port: int = NET.BROKER_PORT,
        router_hb_port: int = NET.BROKER_HB_PORT,
        identity: str = MODULE.BASE_MQ,
        topic_prefix: str = MQ.TOPIC_PREFIX,
    ) -> None:

        self.topic_prefix = topic_prefix
        self.router = router_address
        self.port = router_port
        self.hb_port = router_hb_port
        self.identity = identity

        self.router_addr = f"{NETF.TCP}{self.router}:{self.port}"
        self.router_hb_addr = f"{NETF.TCP}{self.router}:{self.hb_port}"

        self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.DEALER)
        self.hb_socket = self.ctx.socket(zmq.DEALER)

        self.socket.setsockopt(zmq.IDENTITY, self.identity.encode(AIFX.UTF_8))
        self.hb_socket.setsockopt(zmq.IDENTITY, self.identity.encode(AIFX.UTF_8))

        self.socket.connect(self.router_addr)
        self.hb_socket.connect(self.router_hb_addr)

        self.hb_task: asyncio.Task[None] | None = None
        self.hb_stop_event = asyncio.Event()
        self._last_heartbeat = 0.0
        self._started = False
        self._stopped = False

    @staticmethod
    def _ensure_bytes(data: bytes | Frame) -> bytes:
        return data.bytes if isinstance(data, Frame) else data

    @staticmethod
    def _ignore_zmq_teardown(action: Callable[[], None], what: str) -> None:
        try:
            action()
        except zmq.ZMQError as e:
            # expected during shutdown races / already-closed sockets
            print(f"DEBUG: ignoring {what} during shutdown: {type(e).__name__}: {e}")

    def connected(self) -> bool:
        return (time.time() - self._last_heartbeat) < (2 * int(MQ.HEARTBEAT_INTERVAL))

    async def quit(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._started = False
        self.hb_stop_event.set()

        if self.hb_task is not None:
            self.hb_task.cancel()
            try:
                await asyncio.wait_for(self.hb_task, timeout=1.0)
            except asyncio.TimeoutError:
                print("DEBUG: hb_task did not cancel cleanly")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"DEBUG: hb_task exception during quit: {type(e).__name__}: {e}")
            finally:
                self.hb_task = None

        self._ignore_zmq_teardown(
            lambda: self.hb_socket.disconnect(self.router_hb_addr),
            f"hb_socket.disconnect({self.router_hb_addr})",
        )
        self._ignore_zmq_teardown(
            lambda: self.hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        self._ignore_zmq_teardown(
            lambda: self.socket.disconnect(self.router_addr),
            f"socket.disconnect({self.router_addr})",
        )
        self._ignore_zmq_teardown(
            lambda: self.socket.close(linger=0),
            "socket.close(linger=0)",
        )

    async def recv(self) -> MQMsg:
        message_data = None
        message_data = await asyncio.wait_for(
            self.socket.recv(copy=True), timeout=OANDA.TIMEOUT
        )
        if message_data is not None:
            return MQMsg.from_json(self._ensure_bytes(message_data))

    async def send(self, msg: MQMsg) -> None:
        await self.socket.send(msg.to_json())

    def start(self) -> None:
        if self._stopped:
            raise RuntimeError("HydraBaseMQ cannot be restarted after quit()")

        if self._started:
            return

        self.hb_task = asyncio.create_task(self.start_hb_bg(), name=MQF.HEARTBEAT)
        self._started = True

    async def start_hb_bg(self) -> None:
        try:
            while not self.hb_stop_event.is_set():
                msg = MQMsg(
                    sender=self.identity,
                    target=NET.BROKER_HOSTNAME,
                    method=METHOD.HEARTBEAT,
                )
                await self.hb_socket.send(msg.to_json())

                try:
                    message_data = await asyncio.wait_for(
                        self.hb_socket.recv(copy=True),
                        timeout=OANDA.TIMEOUT,
                    )
                    reply = MQMsg.from_json(self._ensure_bytes(message_data))

                    if reply.method == METHOD.HEARTBEAT_REPLY:
                        self._last_heartbeat = time.time()

                except asyncio.CancelledError:
                    raise
                except asyncio.TimeoutError:
                    pass

                await asyncio.sleep(MQ.HEARTBEAT_INTERVAL)

        except asyncio.CancelledError:
            raise

    def topic(self, suffix: str) -> str:
        return f"{self.topic_prefix}.{suffix}"
