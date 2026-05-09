# aifx/client/ClientQt.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DQt import DQtL as QTL

from aifx.utils.AIFxLog import AiFxLog
from aifx.zmq.MQClient import MQClient


class ClientQt(QWidget):
    def __init__(
        self,
        log_level=DEF.DEFAULT_LOG_LEVEL,
        broker_hostname: str = NET.BROKER_HOSTNAME,
        broker_port: int = NET.BROKER_PORT,
        broker_hb_port: int = NET.BROKER_HB_PORT,
        identity: str = MODULE.CLIENT_QT,
    ):
        super().__init__()

        # Console log
        self.log = AiFxLog(client_id=identity, log_level=log_level)
        self.log.info(QTL.AIFX_STARTUP)

        # Only refresh when necessary
        self._was_connected = False

        self.load_ui()
        self.log.info(QTL.UI_LOADED)

        self.mq = MQClient(
            broker_hostname=broker_hostname,
            broker_port=broker_port,
            broker_hb_port=broker_hb_port,
            identity=identity,
            topic_prefix=MQ.TOPIC_PREFIX,
            sub_methods={},
        )
        self.mq.connection_changed.connect(self.set_connection_status)
        self.mq.instruments_received.connect(self.update_instruments)

        self.wire_signals()
        self.log.info(QTL.SIGNALS_WIRED)

        # Defer this, give Qt a chance to start the event loop
        QTimer.singleShot(0, self.start_mq)
        self.log.info(QTL.ENABLING_HEARTBEAT)

        self.log.info(QTL.STARTUP_COMPLETE)

    def set_connection_status(self):
        connected = self.mq.connected()

        if connected:
            self.ui.lbl_connection.setStyleSheet("color: #009900; font-weight: bold;")
            self.ui.lbl_connection.setText(QTL.CONNECTED)

            if not self._was_connected:
                self.mq.get_instruments()

        else:
            self.ui.lbl_connection.setStyleSheet("color: #ff5500; font-weight: bold;")
            self.ui.lbl_connection.setText(QTL.DISCONNECTED)

        self._was_connected = connected

    def load_ui(self):
        loader = QUiLoader()
        path = Path(__file__).resolve().parent / "form.ui"

        ui_file = QFile(path)
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Could not open UI file: {path}")

        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError(f"Could not load UI file: {path}")

        self.ui.setWindowTitle(QTL.AIFX)
        self.ui.lbl_version.setText(f"v{DEF.VERSION}")

    def shutdown(self):
        if getattr(self, "_shutting_down", False):
            return

        self._shutting_down = True

        self.mq.quit()
        self.ui.close()
        self.log.info("Clean shutdown")

    def start_mq(self):
        self.mq.start()
        self.log.info(QTL.MQ_CLIENT_STARTED)

    def wire_signals(self):
        # Wire up an exit button
        self.ui.btn_exit.clicked.connect(self.shutdown)

    def update_instruments(self, instruments):
        self.log.info("Instruments updated")

        self.ui.cb_instrument.clear()

        for instrument in instruments:
            name = instrument["name"]
            display_name = instrument.get("display_name", name)
            pub_port = instrument.get("pub_port")

            self.ui.cb_instrument.addItem(
                f"{display_name} - {name}",
                instrument,
            )


def main():
    app = QApplication(sys.argv)

    widget = ClientQt()
    widget.ui.show()

    app.aboutToQuit.connect(widget.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
