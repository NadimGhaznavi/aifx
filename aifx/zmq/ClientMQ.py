# ai_hydra/utils/HydraClientMQ.py
#
#    AI Hydra
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/ai_hydra
#    Website: https://ai-hydra.readthedocs.io/en/latest
#    License: GPL 3.0
#

# aifx/zmq/ClientMQ.py

from collections.abc import Awaitable, Callable
from typing import Any
import asyncio
import time
import zmq
import zmq.asyncio

from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ, DMQF as MQF
from aifx.constants.DNetwork import DNetwork as NET, DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA

from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.UtilsMQ import UtilsMQ

SubHandler = Callable[[str, dict], Any | Awaitable[Any]]


class ClientMQ:
    def __init__(
        self,
        *,
        broker_hostname: str = NET.BROKER_HOSTNAME,
        broker_port: int = NET.BROKER_PORT,
        broker_hb_port: int = NET.BROKER_HB_PORT,
        identity: str = MODULE.CLIENT_MQ,
        topic_prefix: str = MQ.TOPIC_PREFIX,
        sub_methods: dict[str, SubHandler] | None = None,
    ) -> None:
        self._broker_hostname = broker_hostname
        self._broker_port = broker_port
        self._broker_hb_port = broker_hb_port
        self._identity = identity
        self._topic_prefix = topic_prefix
        self._sub_methods = sub_methods or {}

        self._address = f"{NETF.TCP}{self._broker_hostname}:{self._broker_port}"
        self._hb_address = f"{NETF.TCP}{self._broker_hostname}:{self._broker_hb_port}"

        self._ctx = zmq.asyncio.Context()

        self._socket = self._ctx.socket(zmq.DEALER)
        self._hb_socket = self._ctx.socket(zmq.DEALER)

        self._socket.setsockopt(zmq.IDENTITY, self._identity.encode())
        self._hb_socket.setsockopt(zmq.IDENTITY, self._identity.encode())

        self._socket.connect(self._address)
        self._hb_socket.connect(self._hb_address)

        self._hb_task: asyncio.Task[None] | None = None
        self._hb_stop_event = asyncio.Event()
        self._last_heartbeat = 0.0

        self._started = False
        self._stopped = False

    def connected(self) -> bool:
        return (time.time() - self._last_heartbeat) < (2 * int(MQ.HEARTBEAT_INTERVAL))

    async def recv(self) -> MQMsg:
        message_data = await asyncio.wait_for(
            self._socket.recv(copy=True),
            timeout=OANDA.TIMEOUT,
        )
        return MQMsg.from_json(UtilsMQ.ensure_bytes(message_data))

    async def send(self, msg: MQMsg) -> None:
        await self._socket.send(msg.to_json())

    async def request(self, msg: MQMsg) -> MQMsg:
        await self.send(msg)
        return await self.recv()

    def start(self) -> None:
        if self._started:
            return

        self._started = True
        self._hb_task = asyncio.create_task(
            self.bg_heartbeat(),
            name=MQF.HEARTBEAT,
        )

    async def bg_heartbeat(self) -> None:
        try:
            while not self._hb_stop_event.is_set():
                msg = MQMsg(
                    sender=self._identity,
                    target=NET.BROKER_HOSTNAME,
                    method=METHOD.HEARTBEAT,
                )

                print("Sending heartbeat...")
                await self._hb_socket.send(msg.to_json())

                try:
                    message_data = await asyncio.wait_for(
                        self._hb_socket.recv(copy=True),
                        timeout=OANDA.TIMEOUT,
                    )
                    reply = MQMsg.from_json(UtilsMQ.ensure_bytes(message_data))

                    if reply.method == METHOD.HEARTBEAT_REPLY:
                        self._last_heartbeat = time.time()
                        print("Received heartbeat reply")

                except asyncio.CancelledError:
                    raise
                except asyncio.TimeoutError:
                    print("Heartbeat timed out")

                await asyncio.sleep(MQ.HEARTBEAT_INTERVAL)

        except asyncio.CancelledError:
            raise

    async def quit(self) -> None:
        if self._stopped:
            return

        self._stopped = True
        self._started = False
        self._hb_stop_event.set()

        if self._hb_task is not None:
            self._hb_task.cancel()
            try:
                await asyncio.wait_for(
                    self._hb_task,
                    timeout=MQ.LISTEN_INTERVAL,
                )
            except asyncio.TimeoutError:
                print("DEBUG: Heartbeat task did not cancel cleanly")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(
                    f"DEBUG: Heartbeat task exception during quit: "
                    f"{type(e).__name__}: {e}"
                )
            finally:
                self._hb_task = None

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._hb_socket.disconnect(self._hb_address),
            f"hb_socket.disconnect({self._hb_address})",
        )
        UtilsMQ.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._socket.disconnect(self._address),
            f"socket.disconnect({self._address})",
        )
        UtilsMQ.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.close(linger=0)",
        )

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._ctx.term(),
            "ctx.term()",
        )

    def topic(self, suffix: str) -> str:
        return f"{self._topic_prefix}.{suffix}"
