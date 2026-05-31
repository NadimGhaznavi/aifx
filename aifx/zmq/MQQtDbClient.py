# aifx/zmq/MQQtDbClient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import time
from collections import deque

import zmq
from PySide6.QtCore import QObject, QTimer, Signal

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DNetwork import DNetworkF as NETF
from aifx.constants.DOanda import DOanda as OANDA
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQUtils import MQUtils


class MQQtDbClient(QObject):

    reply_received = Signal(str, object)
    request_failed = Signal(str, object)
    num_rows_received = Signal(object)
    select_all_received = Signal(object)
    select_one_received = Signal(object)
    upsert_received = Signal(object)

    def __init__(
        self,
        log_level: str = DEF.DEFAULT_LOG_LEVEL,
        server_hostname: str = NET.DB_SERVER_HOSTNAME,
        server_port: int = NET.DB_PORT,
        identity: str = MODULE.MQ_DB_CLIENT,
        poll_interval_ms: int = 100,
        timeout_seconds: float = OANDA.TIMEOUT,
    ) -> None:
        super().__init__()

        self.log = AiFxLog(client_id=identity, log_level=log_level)

        self._server_hostname = server_hostname
        self._server_port = server_port
        self._identity = identity
        self._address = f"{NETF.TCP}{server_hostname}:{server_port}"
        self._poll_interval_ms = poll_interval_ms
        self._timeout_seconds = timeout_seconds

        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity.encode())
        self._socket.connect(self._address)

        self._pending_requests: deque[tuple[str, float]] = deque()

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_reply)

        self._timeout_timer = QTimer(self)
        self._timeout_timer.timeout.connect(self._check_timeouts)

        self._started = False
        self._stopped = False

    def num_rows(self, payload: dict) -> bool:
        return self.request(method=METHOD.NUM_ROWS, payload=payload)

    def select_all(self, payload: dict) -> bool:
        return self.request(method=METHOD.SELECT_ALL, payload=payload)

    def select_one(self, payload: dict) -> bool:
        return self.request(method=METHOD.SELECT_ONE, payload=payload)

    def upsert(self, payload: dict) -> bool:
        return self.request(method=METHOD.UPSERT, payload=payload)

    def request(self, method: str, payload: dict | None = None) -> bool:
        msg = MQMsg(
            sender=self._identity,
            target=MODULE.DB_SERVER,
            method=method,
            payload=payload or {},
        )

        try:
            self._socket.send(msg.to_json(), flags=zmq.NOBLOCK)
            self._pending_requests.append((method, time.monotonic()))
            return True
        except zmq.Again:
            return False
        except Exception as e:
            self.log.critical(f"Exception: {e}")
            return False

    def _check_timeouts(self) -> None:
        now = time.monotonic()

        while self._pending_requests:
            method, sent_at = self._pending_requests[0]
            if (now - sent_at) < self._timeout_seconds:
                break

            self._pending_requests.popleft()
            self.request_failed.emit(method, {"error": "timeout"})

    def _emit_reply(self, reply: MQMsg) -> None:
        method = reply.method
        payload = reply.payload

        if method.endswith("_reply"):
            method = method.removesuffix("_reply")

        self.reply_received.emit(method, payload)

        if method == METHOD.NUM_ROWS:
            self.num_rows_received.emit(payload)
        elif method == METHOD.SELECT_ALL:
            self.select_all_received.emit(payload)
        elif method == METHOD.SELECT_ONE:
            self.select_one_received.emit(payload)
        elif method == METHOD.UPSERT:
            self.upsert_received.emit(payload)

    def _poll_reply(self) -> None:
        while True:
            try:
                message_data = self._socket.recv(copy=True, flags=zmq.NOBLOCK)
            except zmq.Again:
                break

            if self._pending_requests:
                self._pending_requests.popleft()

            reply = MQMsg.from_json(MQUtils.ensure_bytes(message_data))
            self._emit_reply(reply)

    def quit(self) -> None:
        if self._stopped:
            return

        self._stopped = True
        self._started = False

        self._poll_timer.stop()
        self._timeout_timer.stop()

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

    def start(self) -> None:
        if self._started:
            return

        self._started = True
        self._stopped = False
        self._poll_timer.start(self._poll_interval_ms)
        self._timeout_timer.start(1000)
