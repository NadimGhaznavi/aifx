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
import sys

import zmq
import zmq.asyncio
import asyncio
import json
import time

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DLogging import DAiFxLog as LOG
from aifx.constants.DMethod import DMethod
from aifx.constants.DMsg import DMsg as MSG
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DAiFx import DAiFx
from aifx.constants.DNetwork import DNetwork as NET, DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA

from aifx.zmq.BaseMQ import BaseMQ
from aifx.zmq.MQMsgBatch import MQMsgBatch
from aifx.zmq.MQMsg import MQMsg
from aifx.utils.AIFxLog import AiFxLog

MsgHandler = Callable[[MQMsg], Any | Awaitable[Any]]


class ServerMQ(BaseMQ):
    def __init__(
        self,
        log_level: LOG = DEF.DEFAULT_LOG_LEVEL,
        addr: str = NET.BROKER_HOSTNAME,
        port: int = NET.BROKER_PORT,
        identity: str = MODULE.SERVER_MQ,
        srv_methods: dict[str, MsgHandler] | None = None,
        topic_prefix: str = MQ.TOPIC_PREFIX,
    ) -> None:

        super().__init__(
            broker_addr=addr,
            broker_port=port,
            identity=identity,
            topic_prefix=topic_prefix,
        )
        self.log = AiFxLog(
            client_id=MODULE.SERVER_MQ,
            log_level=log_level,
            to_console=True,
        )
        self.srv_methods = srv_methods or {}

        # Per topic batch storage
        self._candles_batch = MQMsgBatch()

        # Log the configuration
        self.log.info(f"Broker address set: {addr}")
        self.log.info(f"Broker control port set: {port}")
        self.log.info(f"ZeroMQ identity set: {identity}")

        # Per-Step topic doesn't need batching, it's slow, because of the
        # user defined move_delay
        try:
            self.pub_socket: zmq.asyncio.Socket | None = None
            self.pub_addr = f"{NETF.TCP}*:{pub_port}"
            self.pub_socket = self.ctx.socket(zmq.PUB)

            # Make sure the port is available
            self.pub_socket.bind(self.pub_addr)

        except zmq.ZMQError as e:
            if self.pub_socket is not None:
                self.pub_socket.close(linger=0)
                self.pub_socket = None
            raise RuntimeError(
                f"Failed to bind PUB socket on {self.pub_addr}: {e}"
            ) from e

        self.listen_task: asyncio.Task[None] | None = None
        self.listen_stop_event = asyncio.Event()

        self.check_batches_task: asyncio.Task[None] | None = None
        self.check_batches_stop_event = asyncio.Event()

    async def bg_check_batches(self) -> None:
        try:
            while not self.check_batches_stop_event.is_set():
                await self._flush_timed_out_batch(
                    batch=self._candles_batch,
                    topic=MQ.CANDLES_TOPIC,
                    method=DMethod.CANDLES_BATCH,
                )
                await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.log.critical(f"ERROR: {e}")
            self.log.critical(f"STACKTRACE: {traceback.format_exc()}")

    async def bg_listen(self) -> None:
        try:
            while not self.listen_stop_event.is_set():

                try:
                    message_data = await asyncio.wait_for(
                        self.socket.recv(copy=True),
                        timeout=OANDA.TIMEOUT,
                    )
                    aifx_msg = MQMsg.from_json(self._ensure_bytes(message_data))
                    method = aifx_msg.method
                    handler = self.srv_methods.get(method)
                    if handler is not None:
                        result = handler(aifx_msg)
                        if inspect.isawaitable(result):
                            await result
                    else:
                        print(f"ERROR: Unhandled method {method}")

                except asyncio.TimeoutError:
                    # No message was received, continue...
                    pass
                except Exception as e:
                    print(f"ERROR: {e}")

        except asyncio.CancelledError:
            # normal during shutdown
            raise
        except Exception as e:
            print(f"ERROR: {e}")
            # let the task end; caller can decide what to do
            return

    async def _bg_publish(
        self,
        *,
        topic: str,
        method: str,
        payload: list[dict],
    ) -> None:
        envelope = {
            MSG.SENDER: self.identity,
            MSG.METHOD: method,
            MSG.PAYLOAD: {MSG.MESSAGES: payload},
            MSG.PROTOCOL_VERSION: MSG.PROTOCOL_VERSION,
        }
        topic_b = self.topic(topic).encode(DAiFx.UTF_8)
        data = json.dumps(envelope, separators=(",", ":")).encode(DAiFx.UTF_8)
        await self.pub_socket.send_multipart([topic_b, data])

    async def _enqueue_and_maybe_flush(
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
                MSG.SENDER: self.identity,
                MSG.METHOD: DMethod.COUNTER,
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

    async def _flush_timed_out_batch(
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

    async def publish_candles(self, payload: dict) -> None:
        """
        Received a new message to publish.
        """
        await self._batched_publish(
            batch=self._candles_batch,
            payload=payload,
            topic=MQ.CANDLES_TOPIC,
            method=DMethod.CANDLES_BATCH,
        )

    async def _batched_publish(
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
                    sender=self.identity,
                    method=DMethod.COUNTER,
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
            topic = self.topic(topic).encode(DAiFx.UTF_8)
            data = json.dumps(envelope, separators=(",", ":")).encode(DAiFx.UTF_8)
            await self.pub_socket.send_multipart([topic, data])

    def start(self) -> None:
        super().start()

        if self.listen_task is None:
            self.listen_task = asyncio.create_task(self.bg_listen(), name="listen")

        if self.check_batches_task is None:
            self.check_batches_task = asyncio.create_task(
                self.bg_check_batches(), name="check-batches"
            )
