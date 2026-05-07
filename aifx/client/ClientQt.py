# aifx/client/aifx_qt.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from pathlib import Path
import sys
import asyncio

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader
from qasync import QEventLoop

from aifx.constants.DDef import DDef as DDEF
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ

from aifx.zmq.ClientMQ import ClientMQ


class ClientQt(QWidget):
    def __init__(
        self,
        broker_hostname: str = NET.BROKER_HOSTNAME,
        broker_port: str = NET.BROKER_PORT,
        broker_hb_port: int = NET.BROKER_HB_PORT,
        identity: str = MODULE.CLIENT_QT,
    ):
        # Run Qt parent stack
        print("AiFx starting up...", flush=True)
        super().__init__()

        self.mq = ClientMQ(
            broker_hostname=broker_hostname,
            broker_port=broker_port,
            broker_hb_port=broker_hb_port,
            identity=identity,
            topic_prefix=MQ.TOPIC_PREFIX,
            sub_methods={},
        )
        # Defer this, give Qt a chance to start the event loop
        QTimer.singleShot(0, self.start_mq)

        self.load_ui()
        print("UI Loaded...", flush=True)

        self.wire_signals()
        print("Signals wired...", flush=True)

        print("Houston, we have lift-off!!! Startup complete.", flush=True)

    def load_ui(self):
        try:
            loader = QUiLoader()
            path = Path(__file__).resolve().parent / "form.ui"

            ui_file = QFile(path)
            ui_file.open(QFile.ReadOnly)

            self.ui = loader.load(ui_file)
            ui_file.close()

            # Set the window's title bar
            self.setWindowTitle("AI FX")
            # Set the version string
            self.ui.lbl_version.setText(f"v{DDEF.VERSION}")
        except Exception as e:
            print(f"UI Load failed: {e}", flush=True)

    def start_mq(self):
        self.mq.start()
        print("MQ Client started...", flush=True)

    def wire_signals(self):
        # Wire up an exit button
        self.ui.btn_exit.clicked.connect(self.ui.close)


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    widget = ClientQt()
    widget.ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
