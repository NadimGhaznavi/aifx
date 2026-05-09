# aifx/zmq/ServerMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Any
from collections.abc import Callable, Awaitable
import inspect
import traceback
import time
import asyncio
import zmq
import zmq.asyncio
import json
import time

from aifx.constants.DAiFx import DAiFx as AIFX
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DLogging import DAiFxLog as LOG
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ, DMQF as MQF
from aifx.constants.DMsg import DMsg as MSG
from aifx.constants.DNetwork import DNetwork as NET, DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA

from aifx.utils.AIFxLog import AiFxLog
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQMsgBatch import MQMsgBatch
from aifx.zmq.UtilsMQ import UtilsMQ

MsgHandler = Callable[[MQMsg], Any | Awaitable[Any]]


class ServerMQ:
    def __init__(
        self,
        log_level: LOG = DEF.DEFAULT_LOG_LEVEL,
        hostname: str = NET.BROKER_HOSTNAME,
        port: int = NET.BROKER_PORT,
        hb_port: int = NET.BROKER_HB_PORT,
        identity: str = MODULE.SERVER_MQ,
        topic_prefix: str = MQ.TOPIC_PREFIX,
        srv_methods: dict[str, MsgHandler] | None = None,
    ) -> None:

        self.log = AiFxLog(
            client_id=MODULE.SERVER_MQ,
            log_level=log_level,
            to_console=True,
        )

        self._hostname = hostname
        self._port = port
        self._hb_port = hb_port
        self._topic_prefix = topic_prefix
        self._identity = identity
        self._srv_methods = srv_methods or {}

        # Per topic batch storage
        # self._candles_batch = MQMsgBatch()

        # Log the configuration
        self.log.info(f"Hostname set: {hostname}")
        self.log.info(f"Control port set: {port}")
        self.log.info(f"Heartbeat port set: {hb_port}")
        self.log.info(f"ZeroMQ identity set: {identity}")
        self.log.info(f"Topic prefix set: {topic_prefix}")
        self.log.info(f"Methods registered: {srv_methods}")

        # Addresses
        self._address = f"{NETF.TCP}{self._hostname}:{self._port}"
        self._hb_address = f"{NETF.TCP}{self._hostname}:{self._hb_port}"

        # Sockets
        self._ctx = zmq.asyncio.Context()
        self._socket = self._ctx.socket(zmq.ROUTER)
        self._hb_socket = self._ctx.socket(zmq.ROUTER)

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

        # Connected clients
        self._clients: dict[bytes, float] = {}
        self._clients_lock = asyncio.Lock()

        # Periodically prune stale clients fromt the .clients dictionary
        self._prune_task: asyncio.Task[None] | None = None
        self._prune_stop_event = asyncio.Event()

        self._started = False

    # ----- Static methods -----

    # ----- End of static methods -----

    async def bg_hb_listen(self) -> None:
        try:
            while not self._hb_stop_event.is_set():
                try:
                    frames = await asyncio.wait_for(
                        self._hb_socket.recv_multipart(),
                        timeout=OANDA.TIMEOUT,
                    )

                    routing_id, message_data, route = UtilsMQ.split_router_frames(
                        frames
                    )
                    mq_msg = MQMsg.from_json(message_data)
                    await self._register_client(routing_id)

                    if mq_msg.method == METHOD.HEARTBEAT:
                        self._last_heartbeat = time.time()

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

                        routing_id, message_data, route = UtilsMQ.split_router_frames(
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
                        print(f"Critical exception: {e}")

                else:
                    raise RuntimeError("Socket is not initialized")

        except asyncio.CancelledError:
            # normal during shutdown
            raise
        except Exception as e:
            self.log.critical(f"Caught an exception: {e}")
            print(f"Caught an exception: {e}")
            return

    # Control socket handler loop
    async def bg_prune(self) -> None:
        try:
            while not self._prune_stop_event.is_set():
                await asyncio.sleep(MQ.STALE_CLIENTS_TIMEOUT)

                now = time.time()

                async with self._clients_lock:
                    stale_clients = [...]
                    for routing_id in stale_clients:
                        del self._clients[routing_id]

                for routing_id in stale_clients:
                    # Let the Broker know the client's aged out
                    pass

        except asyncio.CancelledError:
            # normal during shutdown
            raise
        except Exception as e:
            self.log.critical(f"Caught an exception: {e}")
            print(f"Caught an exception: {e}")
            return

    # Return a boolean representing the heartbeat status:
    # True is connected.
    def connected(self) -> bool:
        return (time.time() - self._last_heartbeat) < int(OANDA.TIMEOUT)

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
                    f"DEBUG: Heartbeat task exception during quit: {type(e).__name__}: {e}"
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

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._hb_socket.unbind(self._hb_address),
            f"hb_socket.disconnect({self._hb_address})",
        )
        UtilsMQ.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._socket.unbind(self._address),
            f"socket.disconnect({self._address})",
        )
        UtilsMQ.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.close(linger=0)",
        )

    async def recv(self) -> MQMsg:
        message_data = None
        message_data = await asyncio.wait_for(
            self._socket.recv(copy=True), timeout=OANDA.TIMEOUT
        )
        if message_data is not None:
            return MQMsg.from_json(UtilsMQ.ensure_bytes(message_data))

    async def _register_client(self, routing_id: bytes):
        async with self._clients_lock:
            self._clients[routing_id] = time.time()

    async def send(self, msg: MQMsg) -> None:
        await self._socket.send(msg.to_json())

    async def start(self) -> None:
        if self._started:
            return

        self._socket.bind(self._address)
        self._hb_socket.bind(self._hb_address)

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

    async def UNUSED_flush_timed_out_batch(
        self,
        *,
        batch: MQMsgBatch,
        topic: str,
        method: str,
    ) -> None:
        local_storage = None
        now = time.monotonic()

        await batch.acquire_lock()
        try:
            if batch.has_timed_out(now):
                local_storage = batch.pop_batch()
        finally:
            batch.release_lock()

        if local_storage is not None:
            await self._bg_publish(
                topic=topic,
                method=method,
                payload=local_storage,
            )

    async def UNUSED_publish_candles(self, payload: dict) -> None:
        """
        Received a new message to publish.
        """
        await self._batched_publish(
            batch=self._candles_batch,
            payload=payload,
            topic=MQ.CANDLES_TOPIC,
            method=METHOD.CANDLES_BATCH,
        )

    async def UNUSED_bg_check_batches(self) -> None:
        try:
            while not self.check_batches_stop_event.is_set():
                await self._flush_timed_out_batch(
                    batch=self._candles_batch,
                    topic=MQ.CANDLES_TOPIC,
                    method=METHOD.CANDLES_BATCH,
                )
                await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.log.critical(f"ERROR: {e}")
            self.log.critical(f"STACKTRACE: {traceback.format_exc()}")

    async def UNUSED_batched_publish(
        self, batch: MQMsgBatch, payload: dict, topic: str, method: str
    ) -> None:
        """
        A better name for this function is _enqueue_and_maybe_publish(), but
        that's too verbose, even for me! :)
        """
        local_storage = None
        await batch.acquire_lock()
        try:
            if batch.is_empty():
                count_msg = MQMsg(
                    sender=self._identity,
                    method=METHOD.COUNTER,
                    payload={MSG.COUNT: batch.batch_num()},
                )
                batch.append(count_msg.to_dict())
                batch.append(payload)

            elif batch.batch_size() >= (MQ.MAX_BATCH_SIZE - 1):
                batch.append(payload)
                local_storage = batch.pop_batch()

            else:
                batch.append(payload)

        except Exception as e:
            self.log.critical(f"ERROR: {e}")
            self.log.critical(f"STACKTRACE: {traceback.format_exc()}")

        finally:
            batch.release_lock()

        if local_storage is not None:
            envelope = {
                MSG.SENDER: MODULE.AIFX_BROKER,
                MSG.METHOD: method,
                MSG.PAYLOAD: {MSG.MESSAGES: local_storage},
                MSG.PROTOCOL_VERSION: MSG.PROTOCOL_VERSION,
            }
            topic = self.topic(topic).encode(AIFX.UTF_8)
            data = json.dumps(envelope, separators=(",", ":")).encode(AIFX.UTF_8)
            await self.pub_socket.send_multipart([topic, data])

        # if self.check_batches_task is None:
        #    self.check_batches_task = asyncio.create_task(
        #        self.bg_check_batches(), name="check-batches"
        #    )

    async def UNUSED_bg_publish(
        self,
        *,
        topic: str,
        method: str,
        payload: list[dict],
    ) -> None:
        envelope = {
            MSG.SENDER: self._identity,
            MSG.METHOD: method,
            MSG.PAYLOAD: {MSG.MESSAGES: payload},
            MSG.PROTOCOL_VERSION: MSG.PROTOCOL_VERSION,
        }
        topic_b = self.topic(topic).encode(AIFX.UTF_8)
        data = json.dumps(envelope, separators=(",", ":")).encode(AIFX.UTF_8)
        await self.pub_socket.send_multipart([topic_b, data])

    async def UNUSED_enqueue_and_maybe_flush(
        self,
        lock: asyncio.Lock,
        msgs: list,
        timer_name: str,
        count_name: str,
        payload: dict,
        topic: str,
        method: str,
    ) -> None:

        await lock.acquire()

        timer = getattr(self, timer_name)
        count = getattr(self, count_name)

        # Start batch
        if len(msgs) == 0:
            setattr(self, timer_name, time.monotonic())

            count_msg = {
                MSG.SENDER: self._identity,
                MSG.METHOD: METHOD.COUNTER,
                MSG.PAYLOAD: {MSG.COUNT: count},
                MSG.PROTOCOL_VERSION: MSG.PROTOCOL_VERSION,
            }

            msgs.append(count_msg)
            msgs.append(payload)

            setattr(self, count_name, count + 1)
            lock.release()
            return

        # Normal append
        msgs.append(payload)

        # Size flush
        if len(msgs) >= MQ.MAX_BATCH_SIZE:
            local_storage = msgs.copy()
            msgs.clear()
            setattr(self, timer_name, None)

            lock.release()

            await self._publish(
                topic=topic,
                method=method,
                payload=local_storage,
            )
            return

        lock.release()
