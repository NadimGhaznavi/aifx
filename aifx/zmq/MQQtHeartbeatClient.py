# aifx/zmq/MQQtHeartbeatClient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import time
from typing import Any

import zmq
from PySide6.QtCore import QTimer

from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DNetwork import DNetworkF as NETF
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQUtils import MQUtils

HEARTBEAT_POLL_INTERVAL_MS = 10


class MQQtHeartbeatClient:
    _ctx: Any
    _identity: str
    log: AiFxLog

    def _init_heartbeat(
        self,
        server_hostname: str | None,
        server_hb_port: int | None,
        target: str | None,
    ) -> None:
        self._server_hb_port = server_hb_port
        self._heartbeat_target = target
        self._hb_address = f"{NETF.TCP}{server_hostname}:{server_hb_port}"

        self._hb_socket = self._ctx.socket(zmq.DEALER)
        self._hb_socket.setsockopt(zmq.IDENTITY, self._identity.encode())
        self._hb_socket.connect(self._hb_address)

        self._last_heartbeat = 0.0
        self._pending_heartbeat_at: float | None = None
        self._heartbeat_latency_ms: float | None = None
        self._last_connected: bool | None = None

        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._heartbeat_tick)

        self._poll_hb_timer = QTimer(self)
        self._poll_hb_timer.timeout.connect(self._poll_heartbeat_reply)

    def _close_heartbeat(self, disconnect: bool = False) -> None:
        self._hb_timer.stop()
        self.log.info("Heartbeat timer stopped")

        self._poll_hb_timer.stop()
        self.log.info("Heartbeat poll timer stopped")

        if disconnect:
            MQUtils.ignore_zmq_teardown(
                lambda: self._hb_socket.disconnect(self._hb_address),
                f"hb_socket.disconnect({self._hb_address})",
            )

        MQUtils.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

    def _start_heartbeat(self) -> None:
        self._hb_timer.start(int(MQ.HEARTBEAT_INTERVAL) * 1000)
        self._poll_hb_timer.start(HEARTBEAT_POLL_INTERVAL_MS)
        self._heartbeat_tick()

    def connected(self) -> bool:
        return (time.monotonic() - self._last_heartbeat) < (
            2 * int(MQ.HEARTBEAT_INTERVAL)
        )

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
            target=self._heartbeat_target,
            method=METHOD.HEARTBEAT,
        )
        try:
            self._hb_socket.send(msg.to_json(), flags=zmq.NOBLOCK)
            self._pending_heartbeat_at = now
        except zmq.Again:
            pass

        self._update_connection_state()

    def _poll_heartbeat_reply(self) -> None:
        latency_ms = None

        while True:
            try:
                message_data = self._hb_socket.recv(copy=True, flags=zmq.NOBLOCK)
            except zmq.Again:
                break

            reply = MQMsg.from_json(MQUtils.ensure_bytes(message_data))

            if reply.method == METHOD.HEARTBEAT_REPLY:
                now = time.monotonic()
                self._last_heartbeat = now
                if self._pending_heartbeat_at is not None:
                    latency_ms = (now - self._pending_heartbeat_at) * 1000.0
                    self._heartbeat_latency_ms = latency_ms
                    self._pending_heartbeat_at = None

        self._update_connection_state(latency_ms=latency_ms)

    def _update_connection_state(self, latency_ms: float | None = None) -> None:
        now_connected = self.connected()
        state_changed = now_connected != self._last_connected

        if state_changed:
            self._last_connected = now_connected

        if not now_connected:
            self._heartbeat_latency_ms = None
            latency_ms = None

        if state_changed or latency_ms is not None:
            self._emit_heartbeat_status(now_connected, latency_ms)

    def _emit_heartbeat_status(
        self,
        connected: bool,
        latency_ms: float | None,
    ) -> None:
        raise NotImplementedError
