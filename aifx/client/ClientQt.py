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

from aifx.constants.DDef import DDef as DDEF
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DQt import DQtL as QTL

from aifx.zmq.ClientMQ import ClientMQ


class ClientQt(QWidget):
    def __init__(
        self,
        broker_hostname: str = NET.BROKER_HOSTNAME,
        broker_port: int = NET.BROKER_PORT,
        broker_hb_port: int = NET.BROKER_HB_PORT,
        identity: str = MODULE.CLIENT_QT,
    ):
        print(QTL.AIFX_STARTUP, flush=True)
        super().__init__()

        self.load_ui()
        print(QTL.UI_LOADED, flush=True)

        self.mq = ClientMQ(
            broker_hostname=broker_hostname,
            broker_port=broker_port,
            broker_hb_port=broker_hb_port,
            identity=identity,
            topic_prefix=MQ.TOPIC_PREFIX,
            sub_methods={},
        )
        self.mq.connection_changed.connect(self.set_connection_status)

        self.wire_signals()
        print(QTL.SIGNALS_WIRED, flush=True)

        # Defer this, give Qt a chance to start the event loop
        QTimer.singleShot(0, self.start_mq)
        print(QTL.ENABLING_HEARTBEAT, flush=True)

        print(QTL.STARTUP_COMPLETE, flush=True)

    def set_connection_status(self):
        if self.mq.connected():
            self.ui.lbl_connection.setStyleSheet("color: #009900; font-weight: bold;")
            self.ui.lbl_connection.setText(QTL.CONNECTED)
        else:
            self.ui.lbl_connection.setStyleSheet("color: #ff5500; font-weight: bold;")
            self.ui.lbl_connection.setText(QTL.DISCONNECTED)


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
        self.ui.lbl_version.setText(f"v{DDEF.VERSION}")

    def shutdown(self):
        if getattr(self, "_shutting_down", False):
            return

        self._shutting_down = True

        self.mq.quit()
        self.ui.close()
        print("Clean shutdown")

    def start_mq(self):
        self.mq.start()
        print(QTL.MQ_CLIENT_STARTED, flush=True)

    def wire_signals(self):
        # Wire up an exit button
        self.ui.btn_exit.clicked.connect(self.shutdown)


def main():
    app = QApplication(sys.argv)

    widget = ClientQt()
    widget.ui.show()

    app.aboutToQuit.connect(widget.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
