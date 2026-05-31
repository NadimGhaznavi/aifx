# aifx/zmq/MQQtBrainClient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import zmq
from PySide6.QtCore import QObject, Signal

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DNetwork import DNetwork as NET
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQQtHeartbeatClient import MQQtHeartbeatClient
from aifx.zmq.MQUtils import MQUtils


class MQQtBrainClient(QObject, MQQtHeartbeatClient):

    brain_status_changed = Signal(bool, object)

    def __init__(
        self,
        log_level: str = DEF.DEFAULT_LOG_LEVEL,
        server_hostname: str = NET.BRAIN_HOSTNAME,
        server_hb_port: int = NET.BRAIN_HB_PORT,
        identity: str = MODULE.CLIENT_QT,
    ) -> None:
        super().__init__()

        self.log = AiFxLog(client_id=identity, log_level=log_level)

        self._server_hostname = server_hostname
        self._server_hb_port = server_hb_port
        self._identity = identity

        self._ctx = zmq.Context()
        self._init_heartbeat(
            server_hostname=server_hostname,
            server_hb_port=server_hb_port,
            target=MODULE.BRAIN,
        )

        self._started = False
        self._stopped = False

    def quit(self) -> None:
        if self._stopped:
            return

        self._stopped = True
        self._started = False

        self._close_heartbeat(disconnect=True)
        MQUtils.ignore_zmq_teardown(
            lambda: self._ctx.destroy(linger=0),
            "ctx.destroy(linger=0)",
        )

    def start(self) -> None:
        if self._started:
            return

        self._started = True
        self._stopped = False
        self._start_heartbeat()

    def _emit_heartbeat_status(
        self,
        connected: bool,
        latency_ms: float | None,
    ) -> None:
        self.brain_status_changed.emit(connected, latency_ms)
