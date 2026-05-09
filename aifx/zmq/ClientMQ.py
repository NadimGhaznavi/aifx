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

from collections.abc import Callable
from typing import Any
import time
import zmq
from PySide6.QtCore import QObject, QTimer, Signal

from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DNetwork import DNetwork as NET, DNetworkF as NETF
from aifx.constants.DQt import DQtL as QTL

from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.UtilsMQ import UtilsMQ

SubHandler = Callable[[str, dict], Any]


class ClientMQ(QObject):

    connection_changed = Signal(bool)

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
        super().__init__()
        self._broker_hostname = broker_hostname
        self._broker_port = broker_port
        self._broker_hb_port = broker_hb_port
        self._identity = identity
        self._topic_prefix = topic_prefix
        self._sub_methods = sub_methods or {}

        self._address = f"{NETF.TCP}{self._broker_hostname}:{self._broker_port}"
        self._hb_address = f"{NETF.TCP}{self._broker_hostname}:{self._broker_hb_port}"

        self._ctx = zmq.Context()

        self._socket = self._ctx.socket(zmq.DEALER)
        self._hb_socket = self._ctx.socket(zmq.DEALER)

        self._socket.setsockopt(zmq.IDENTITY, self._identity.encode())
        self._hb_socket.setsockopt(zmq.IDENTITY, self._identity.encode())

        self._socket.connect(self._address)
        self._hb_socket.connect(self._hb_address)

        self._last_heartbeat = 0.0
        self._last_connected = None

        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._heartbeat_tick)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_heartbeat_reply)

        self._started = False
        self._stopped = False

    def connected(self) -> bool:
        return (time.time() - self._last_heartbeat) < (2 * int(MQ.HEARTBEAT_INTERVAL))

    def _heartbeat_tick(self) -> None:
        msg = MQMsg(
            sender=self._identity,
            target=NET.BROKER_HOSTNAME,
            method=METHOD.HEARTBEAT,
        )
        print(QTL.SENDING_HEARTBEAT)
        try:
            self._hb_socket.send(msg.to_json(), flags=zmq.NOBLOCK)
        except zmq.Again:
            pass

        self._update_connection_state()

    def _poll_heartbeat_reply(self) -> None:
        while True:
            print(QTL.POLLING_HEARTBEAT_REPLY)
            try:
                print(QTL.POLLING_HEARTBEAT_REPLY, flush=True)
                message_data = self._hb_socket.recv(copy=True, flags=zmq.NOBLOCK)
            except zmq.Again:
                break

            reply = MQMsg.from_json(UtilsMQ.ensure_bytes(message_data))

            if reply.method == METHOD.HEARTBEAT_REPLY:
                print(QTL.HEARTBEAT_REPLY_RECEIVED)
                self._last_heartbeat = time.time()

        self._update_connection_state()

    def quit(self) -> None:
        if self._stopped:
            print("ClientMQ.quit(): Already stopped", flush=True)
            return

        self._stopped = True
        self._started = False

        self._hb_timer.stop()
        print("ClientMQ.quit(): Heartbeat timer stopped", flush=True)

        self._poll_timer.stop()
        print("ClientMQ.quit(): Poll timer stopped", flush=True)

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._hb_socket.close(linger=0),
            "hb_socket.close(linger=0)",
        )

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.disconnect(linger=0)",
        )
        UtilsMQ.ignore_zmq_teardown(
            lambda: self._socket.close(linger=0),
            "socket.close(linger=0)",
        )

        UtilsMQ.ignore_zmq_teardown(
            lambda: self._ctx.destroy(linger=0),
            "ctx.destroy(linger=0)",
        )

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
        self._poll_timer.start(1000)
        self._heartbeat_tick()

    def topic(self, suffix: str) -> str:
        return f"{self._topic_prefix}.{suffix}"

    def _update_connection_state(self) -> None:
        now_connected = self.connected()

        if now_connected != self._last_connected:
            self._last_connected = now_connected
            self.connection_changed.emit(now_connected)
