# aifx/zmq/ServerMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
import inspect
import json
import time
import traceback
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

import zmq
import zmq.asyncio

from aifx.constants.DAiFx import DAiFx as AIFX
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMQ import DMQF as MQF
from aifx.constants.DMQ import DMQEvent
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DNetwork import DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQEvent import MQEvent
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQUtils import MQUtils

MsgHandler = Callable[[MQMsg], Any | Awaitable[Any]]


class MQServer:
    def __init__(
        self,
        log_level: str = DEF.DEFAULT_LOG_LEVEL,
        hostname: str = NET.BROKER_HOSTNAME,
        port: int = NET.BROKER_PORT,
        hb_port: int = NET.BROKER_HB_PORT,
        pub_port: int = NET.BROKER_PUB_PORT,
        identity: str = MODULE.SERVER_MQ,
        topic_prefix: str = MQ.TOPIC_PREFIX,
        srv_methods: Mapping[str, MsgHandler] | None = None,
    ) -> None:

        self.log = AiFxLog(
            client_id=MODULE.SERVER_MQ,
            log_level=log_level,
            to_console=True,
        )

        self._hostname = hostname
        self._port = port
        self._hb_port = hb_port
        self._pub_port = pub_port
        self._topic_prefix = topic_prefix
        self._identity = identity
        self._srv_methods = srv_methods or {}

        # Per topic batch storage
        # self._candles_batch = MQMsgBatch()

        # Log the configuration
        self.log.info(f"Hostname set: {hostname}")
        self.log.info(f"Control port set: {port}")
        self.log.info(f"Heartbeat port set: {hb_port}")
        self.log.info(f"PUB port set: {pub_port}")
        self.log.info(f"ZeroMQ identity set: {identity}")
        self.log.info(f"Topic prefix set: {topic_prefix}")
        methods = list(self._srv_methods.keys())
        self.log.info(f"Methods registered: {methods}")

        # Addresses
        self._address = f"{NETF.TCP}{self._hostname}:{self._port}"
        self._hb_address = f"{NETF.TCP}{self._hostname}:{self._hb_port}"
        self._pub_address = f"{NETF.TCP}{self._hostname}:{self._pub_port}"

        # Sockets
        self._ctx = zmq.asyncio.Context()
        self._socket = self._ctx.socket(zmq.ROUTER)
        self._hb_socket = self._ctx.socket(zmq.ROUTER)
        self._pub_socket = self._ctx.socket(zmq.PUB)
        self._pub_socket.linger = 0

        # ----- Tasks and Stop Events -----
        # Monitor the ROUTER/DEALER control port
        self._listen_task: asyncio.Task[None] | None = None
        self._listen_stop_event = asyncio.Event()

        # Monitor the ROUTER/DEALER heartbeat port
        self._hb_task: asyncio.Task[None] | None = None
        self._hb_stop_event = asyncio.Event()
        self._last_heartbeat = 0.0

        # Monitor the batched messages queues
        # self.check_batches_task: asyncio.Task[None] | None = None
        # self.check_batches_stop_event = asyncio.Event()

        # General purpose queue to the Broker app
        self.event_queue: asyncio.Queue[MQEvent] = asyncio.Queue()

        # Connected clients
        self._clients: dict[bytes, float] = {}
        self._clients_lock = asyncio.Lock()

        # Periodically prune stale clients fromt the .clients dictionary
        self._prune_task: asyncio.Task[None] | None = None
        self._prune_stop_event = asyncio.Event()

        self._started = False

    async def bg_hb_listen(self) -> None:
        try:
            while not self._hb_stop_event.is_set():
                try:
                    frames = await asyncio.wait_for(
                        self._hb_socket.recv_multipart(),
                        timeout=OANDA.TIMEOUT,
                    )

                    routing_id, message_data, route = MQUtils.split_router_frames(
                        frames
                    )
                    mq_msg = MQMsg.from_json(message_data)
                    await self._register_client(routing_id)

                    if mq_msg.method == METHOD.HEARTBEAT:
                        self._last_heartbeat = time.monotonic()

                        reply = MQMsg(
                            sender=self._identity,
                            target=mq_msg.sender,
                            method=METHOD.HEARTBEAT_REPLY,
                        )

                        await self._hb_socket.send_multipart(route + [reply.to_json()])

                except asyncio.TimeoutError:
                    pass

                await asyncio.sleep(MQ.HEARTBEAT_INTERVAL)

        except asyncio.CancelledError:
            raise

    # Control socket handler loop
    async def bg_listen(self) -> None:
        try:
            while not self._listen_stop_event.is_set():

                if self._socket is not None:
                    try:
                        frames = await asyncio.wait_for(
                            self._socket.recv_multipart(),
                            timeout=OANDA.TIMEOUT,
                        )

                        routing_id, message_data, route = MQUtils.split_router_frames(
                            frames
                        )
                        await self._register_client(routing_id)

                        # Deserialize to HydraMsg
                        mq_msg = MQMsg.from_json(message_data)

                        # Handle the message
                        if mq_msg.method not in self._srv_methods:
                            raise ValueError(f"Unhandled method: {mq_msg.method}")

                        result = self._srv_methods[mq_msg.method](mq_msg)

                        if inspect.isawaitable(result):
                            result = await result

                        reply = MQMsg(
                            sender=self._identity,
                            target=mq_msg.sender,
                            method=f"{mq_msg.method}_reply",
                            payload=result,
                        )
                        await self._socket.send_multipart(route + [reply.to_json()])
                    except asyncio.TimeoutError:
                        # No message received, continue
                        pass
                    except Exception as e:
                        self.log.critical(f"Critical exception: {e}")
                        self.log.critical(f"STACKTRACE: {traceback.format_exc()}")
                        print(f"Critical exception: {e}")

                else:
                    raise RuntimeError("Socket is not initialized")

        except asyncio.CancelledError:
            # normal during shutdown
            raise
        except Exception as e:
            self.log.critical(f"Caught an exception: {e}")
            self.log.critical(f"STACKTRACE: {traceback.format_exc()}")
            return

    # Pruning loop
    async def bg_prune(self) -> None:
        try:
            while not self._prune_stop_event.is_set():
                await asyncio.sleep(MQ.PRUNE_INTERVAL)

                now = time.monotonic()

                async with self._clients_lock:
                    stale_clients = [
                        routing_id
                        for routing_id, last_seen in self._clients.items()
                        if (now - last_seen) > MQ.CLIENT_TIMEOUT
                    ]

                for routing_id in stale_clients:
                    await self._remove_client(routing_id)

        except asyncio.CancelledError:
            # normal during shutdown
            raise
        except Exception as e:
            self.log.critical(f"Caught an exception: {e}")
            self.log.critical(f"STACKTRACE: {traceback.format_exc()}")
            return

    # Return a boolean representing the heartbeat status:
    # True is connected.
    def connected(self) -> bool:
        return (time.monotonic() - self._last_heartbeat) < int(OANDA.TIMEOUT)

    async def publish(self, topic: str, payload: dict) -> None:
        topic_b = topic.encode(AIFX.UTF_8)
        data_b = json.dumps(payload, separators=(",", ":")).encode(AIFX.UTF_8)
        await self._pub_socket.send_multipart([topic_b, data_b])
        # self.log.debug(f"Published {topic} candle @ {timestamp}")

    async def quit(self) -> None:
        if not self._started:
            return
        self._started = False

        self._hb_stop_event.set()
        if self._hb_task is not None:
            self._hb_task.cancel()
            try:
                await asyncio.wait_for(self._hb_task, timeout=MQ.LISTEN_INTERVAL)
            except asyncio.TimeoutError:
                print("DEBUG: Heartbeat task did not cancel cleanly")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(
                    "DEBUG: Heartbeat task exception during quit: ",
                    f"{type(e).__name__}: {e}",
                )
            finally:
                self._hb_task = None

        self._listen_stop_event.set()
        if self._listen_task is not None:
            self._listen_task.cancel()
            try:
                await asyncio.wait_for(self._listen_task, timeout=MQ.LISTEN_INTERVAL)
            except asyncio.TimeoutError:
                print("DEBUG: Listen task did not cancel cleanly")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(
                    f"DEBUG: Listen task exception during quit: {type(e).__name__}: {e}"
                )
            finally:
                self._listen_task = None

        MQUtils.ignore_zmq_teardown(
            lambda: self._hb_socket.unbind(self._hb_address),
            f"hb_socket.disconnect({self._hb_address})",
        )
        MQUtils.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        MQUtils.ignore_zmq_teardown(
            lambda: self._socket.unbind(self._address),
            f"socket.disconnect({self._address})",
        )
        MQUtils.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.close(linger=0)",
        )

        MQUtils.ignore_zmq_teardown(
            lambda: self._pub_socket.unbind(self._pub_address),
            f"pub_socket.unbind({self._pub_address})",
        )

        MQUtils.ignore_zmq_teardown(
            lambda: self._pub_socket.close(linger=0),
            "pub_socket.close(linger=0)",
        )

    async def recv(self) -> MQMsg:
        message_data = None
        message_data = await asyncio.wait_for(
            self._socket.recv(copy=True), timeout=OANDA.TIMEOUT
        )
        if message_data is not None:
            return MQMsg.from_json(MQUtils.ensure_bytes(message_data))

    async def _register_client(self, routing_id: bytes):
        async with self._clients_lock:
            if routing_id in self._clients:
                self._clients[routing_id] = time.monotonic()
                return

            self._clients[routing_id] = time.monotonic()

        self.event_queue.put_nowait(
            MQEvent(event_type=DMQEvent.CLIENT_ADDED, routing_id=routing_id)
        )

    async def _remove_client(self, routing_id: bytes) -> None:
        async with self._clients_lock:
            self._clients.pop(routing_id, None)

        self.event_queue.put_nowait(
            MQEvent(event_type=DMQEvent.CLIENT_REMOVED, routing_id=routing_id)
        )

    async def send(self, msg: MQMsg) -> None:
        await self._socket.send(msg.to_json())

    async def start(self) -> None:
        if self._started:
            return

        self._socket.bind(self._address)
        self._hb_socket.bind(self._hb_address)
        self._pub_socket.bind(self._pub_address)

        self._started = True
        self._hb_task = asyncio.create_task(self.bg_hb_listen(), name=MQF.HEARTBEAT)
        self._listen_task = asyncio.create_task(self.bg_listen(), name=MQF.CONTROL)
        self._prune_task = asyncio.create_task(self.bg_prune(), name=MQF.PRUNING)

        await asyncio.gather(
            self._hb_task,
            self._listen_task,
            self._prune_task,
        )

    def topic(self, suffix: str) -> str:
        return f"{self._topic_prefix}.{suffix}"
