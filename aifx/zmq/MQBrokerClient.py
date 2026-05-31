# ai_hydra/utils/MQClient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com/
#    License: GPL 3.0
#

import time
from collections.abc import Callable
from typing import Any

import zmq
from PySide6.QtCore import QObject, QTimer, Signal

from aifx.constants.DAiFx import DAiFx as AIFX
from aifx.constants.DCandle import DCandleF as CANDLEF
from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMQ import DMQF as MQF
from aifx.constants.DNetwork import DNetworkF as NETF
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQUtils import MQUtils

SubHandler = Callable[[str, dict], Any]


class MQBrokerClient(QObject):

    candle_received = Signal(str, object)
    broker_status_changed = Signal(bool, object)
    instruments_received = Signal(object)
    feed_started = Signal(object)
    recent_candles = Signal(str, object)

    def __init__(
        self,
        log_level: str = DEF.DEFAULT_LOG_LEVEL,
        server_hostname: str | None = None,
        server_port: int | None = None,
        server_hb_port: int | None = None,
        server_pub_port: int | None = None,
        identity: str = MODULE.MQ_BROKER_CLIENT,
        topic_prefix: str = MQ.TOPIC_PREFIX,
        sub_methods: dict[str, SubHandler] | None = None,
    ) -> None:
        super().__init__()

        # Console log
        self.log = AiFxLog(client_id=MODULE.MQ_BROKER_CLIENT, log_level=log_level)

        self._server_hostname = server_hostname
        self._server_port = server_port
        self._server_hb_port = server_hb_port
        self._server_pub_port = server_pub_port
        self._identity = identity
        self._topic_prefix = topic_prefix
        self._sub_methods = sub_methods or {}

        self._address = f"{NETF.TCP}{server_hostname}:{server_port}"
        self._hb_address = f"{NETF.TCP}{server_hostname}:{server_hb_port}"
        self._sub_address = f"{NETF.TCP}{server_hostname}:{server_pub_port}"

        self._ctx = zmq.Context()

        self._socket = self._ctx.socket(zmq.DEALER)
        self._hb_socket = self._ctx.socket(zmq.DEALER)
        self._sub_socket = self._ctx.socket(zmq.SUB)

        self._socket.setsockopt(zmq.IDENTITY, self._identity.encode())
        self._hb_socket.setsockopt(zmq.IDENTITY, self._identity.encode())

        self._socket.connect(self._address)
        self._timer = QTimer(self)
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_control_reply)

        self._hb_socket.connect(self._hb_address)
        self._last_heartbeat = 0.0
        self._pending_heartbeat_at: float | None = None
        self._broker_latency_ms: float | None = None
        self._last_connected: bool | None = None
        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._heartbeat_tick)

        self._poll_hb_timer = QTimer(self)
        self._poll_hb_timer.timeout.connect(self._poll_heartbeat_reply)

        self._sub_socket.connect(self._sub_address)
        self._sub_timer = QTimer(self)
        self._sub_timer.timeout.connect(self._bg_sub_listen)

        self._started = False
        self._stopped = False

    def _bg_sub_listen(self) -> None:
        while True:
            try:
                parts = self._sub_socket.recv_multipart(flags=zmq.NOBLOCK)
            except zmq.Again:
                break

            if len(parts) != 2:
                self.log.warning(f"Invalid SUB frame count: {len(parts)}")
                continue

            topic_b, payload_b = parts

            topic = topic_b.decode(AIFX.UTF_8)
            payload = MQUtils.decode_json(payload_b)

            handler = self._sub_methods.get(topic)

            if handler is None:
                self.log.warning(f"No SUB handler for topic: {topic}")
                continue

            handler(topic, payload)

    def candle_topic(self, instrument: str) -> str:
        return self.topic(f"candles.{instrument}")

    def connected(self) -> bool:
        return (time.monotonic() - self._last_heartbeat) < (
            2 * int(MQ.HEARTBEAT_INTERVAL)
        )

    def get_instruments(self) -> bool:
        msg = MQMsg(
            sender=self._identity,
            target=self._server_hostname,
            method=METHOD.GET_INSTRUMENTS,
        )
        try:
            self._socket.send(msg.to_json(), flags=zmq.NOBLOCK)
            return True
        except Exception as e:
            self.log.critical(f"Exception: {e}")
            return False

    def get_recent_candles(self, topic, instrument, count) -> bool:
        msg = MQMsg(
            sender=self._identity,
            target=self._server_hostname,
            method=METHOD.GET_RECENT_CANDLES,
            payload={
                C_CAND.INSTRUMENT: instrument[C_INST.NAME],
                DBF.LIMIT: count,
                INSF.TOPIC: topic,
            },
        )
        try:
            self._socket.send(msg.to_json(), flags=zmq.NOBLOCK)
            return True
        except Exception as e:
            self.log.critical(f"Exception: {e}")
            return False

    def _handle_control_reply(self, reply: MQMsg) -> None:
        if reply.method == METHOD.GET_INSTRUMENTS_REPLY:
            self.instruments_received.emit(reply.payload[MQF.INSTRUMENTS])
            return

        elif reply.method == METHOD.START_FEED_REPLY:
            self.feed_started.emit(reply.payload)
            return

        elif reply.method == METHOD.GET_RECENT_CANDLES_REPLY:
            self.recent_candles.emit(
                reply.payload[INSF.TOPIC],
                reply.payload[CANDLEF.CANDLES],
            )
            return

        self.log.critical(f"Unhandled control reply: {reply.method}")

    def _heartbeat_tick(self) -> None:
        now = time.monotonic()
        if self._pending_heartbeat_at is not None:
            pending_age = now - self._pending_heartbeat_at
            if pending_age < (2 * int(MQ.HEARTBEAT_INTERVAL)):
                self._update_connection_state()
                return
            self._pending_heartbeat_at = None

        msg = MQMsg(
            sender=self._identity,
            target=self._server_hostname,
            method=METHOD.HEARTBEAT,
        )
        # self.log.debug(QTL.SENDING_HEARTBEAT)
        try:
            self._hb_socket.send(msg.to_json(), flags=zmq.NOBLOCK)
            self._pending_heartbeat_at = now
        except zmq.Again:
            pass

        self._update_connection_state()

    def _poll_control_reply(self) -> None:
        while True:
            try:
                message_data = self._socket.recv(copy=True, flags=zmq.NOBLOCK)
            except zmq.Again:
                break

            reply = MQMsg.from_json(MQUtils.ensure_bytes(message_data))
            self._handle_control_reply(reply)

    def _poll_heartbeat_reply(self) -> None:
        while True:
            # self.log.debug(QTL.POLLING_HEARTBEAT_REPLY)
            try:
                # self.log.debug(QTL.POLLING_HEARTBEAT_REPLY)
                message_data = self._hb_socket.recv(copy=True, flags=zmq.NOBLOCK)
            except zmq.Again:
                break

            reply = MQMsg.from_json(MQUtils.ensure_bytes(message_data))

            if reply.method == METHOD.HEARTBEAT_REPLY:
                # self.log.debug(QTL.HEARTBEAT_REPLY_RECEIVED)
                now = time.monotonic()
                self._last_heartbeat = now
                if self._pending_heartbeat_at is not None:
                    self._broker_latency_ms = (
                        now - self._pending_heartbeat_at
                    ) * 1000.0
                    self._pending_heartbeat_at = None

        self._update_connection_state()

    def quit(self) -> None:
        if self._stopped:
            self.log.warning("ClientMQ.quit(): Already stopped")
            return

        self._stopped = True
        self._started = False

        self._hb_timer.stop()
        self.log.info("Heartbeat timer stopped")

        self._poll_hb_timer.stop()
        self.log.info("Heartbeat poll timer stopped")

        self._poll_timer.stop()
        self.log.info("Control poll timer stopped")

        self._sub_timer.stop()
        self.log.info("SUB poll timer stopped")

        MQUtils.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.close(linger=0)",
        )

        MQUtils.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        MQUtils.ignore_zmq_teardown(
            lambda: self._sub_socket.close(linger=0),
            "sub_socket.close(linger=0)",
        )

        MQUtils.ignore_zmq_teardown(
            lambda: self._ctx.destroy(linger=0),
            "ctx.destroy(linger=0)",
        )

    def register_sub_handler(self, topic: str, handler: SubHandler) -> None:
        self.log.info(f"Registering SUB handler: {topic}")
        self._sub_methods[topic] = handler

    def send(self, msg: MQMsg) -> bool:
        try:
            self._socket.send(msg.to_json(), flags=zmq.NOBLOCK)
            return True
        except zmq.Again:
            return False

    def start(self) -> None:
        if self._started:
            return

        self._started = True
        self._hb_timer.start(int(MQ.HEARTBEAT_INTERVAL) * 1000)
        self._poll_hb_timer.start(1000)
        self._poll_timer.start(100)
        self._sub_timer.start(100)
        self._heartbeat_tick()

    def start_feed(self, instrument: dict) -> bool:
        msg = MQMsg(
            sender=self._identity,
            target=MODULE.BROKER,
            method=METHOD.START_FEED,
            payload=instrument,
        )
        return self.send(msg)

    def subscribe(self, topic: str) -> None:
        self.log.info(f"Subscribing: {topic}")
        self._sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def topic(self, suffix: str) -> str:
        return f"{self._topic_prefix}.{suffix}"

    def _update_connection_state(self) -> None:
        now_connected = self.connected()

        if now_connected != self._last_connected:
            self._last_connected = now_connected

        if now_connected:
            latency_ms = self._broker_latency_ms
        else:
            self._broker_latency_ms = None
            latency_ms = None
        self.broker_status_changed.emit(now_connected, latency_ms)

    def unsubscribe(self, topic: str) -> None:
        self.log.info(f"Unsubscribing: {topic}")
        self._sub_socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)
