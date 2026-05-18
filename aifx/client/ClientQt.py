# aifx/client/ClientQt.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import json
import sys
from pathlib import Path

from PySide6.QtCore import QFile, Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DQt import DQtL as QTL
from aifx.db.ClientDb import ClientDb
from aifx.db.DbMgr import DbMgr
from aifx.forex.Candle import Candle
from aifx.forex.RecentCandlesModel import RecentCandlesModel
from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQClient import MQClient

# Number of candles to cache for Plotly
RECENT_CANDLES_COLUMN_PADDING = 50


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(32, 32, 32))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(24, 24, 24))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(36, 36, 36))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(48, 48, 48))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(96, 127, 58))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)

    app.setStyleSheet("""
        QWidget {
            background-color: #202020;
            color: #eeeeee;
        }
        QLabel {
            color: #eeeeee;
        }
        QPushButton, QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #555555;
            color: #eeeeee;
            padding: 4px 8px;
        }
        QPushButton:hover, QComboBox:hover {
            border-color: #7a9f45;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        QComboBox QAbstractItemView {
            background-color: #242424;
            color: #eeeeee;
            selection-background-color: #607f3a;
            selection-color: #ffffff;
        }
        QTableView {
            background-color: #181818;
            alternate-background-color: #242424;
            color: #eeeeee;
            gridline-color: #3a3a3a;
            selection-background-color: #607f3a;
            selection-color: #ffffff;
        }
        QHeaderView::section {
            background-color: #2d2d2d;
            color: #eeeeee;
            border: 1px solid #444444;
            padding: 4px;
        }
        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: #202020;
        }
    """)


class ClientQt(QWidget):
    def __init__(
        self,
        log_level=DEF.DEFAULT_LOG_LEVEL,
        broker_hostname: str = NET.BROKER_HOSTNAME,
        broker_port: int = NET.BROKER_PORT,
        broker_hb_port: int = NET.BROKER_HB_PORT,
        broker_pub_port: int = NET.BROKER_PUB_PORT,
        identity: str = MODULE.CLIENT_QT,
    ):
        super().__init__()
        self._broker_hostname = broker_hostname

        # Console log
        self.log = AiFxLog(client_id=identity, log_level=log_level)
        self.log.info(QTL.AIFX_STARTUP)

        # Only refresh when necessary
        self._was_connected = False

        # In memory dictionary of instruments
        self._instruments: dict[str, dict] = {}

        # In memory client data cache
        self.db_mgr = DbMgr(db_type=DBF.CACHE, log_level=log_level)
        self.client_db = ClientDb(db_mgr=self.db_mgr, log_level=log_level)

        # Load the UI
        self.load_ui()
        self.setup_recent_candles_table()
        # Prepare the plotting widget
        self.setup_plot()
        self.log.info(QTL.UI_LOADED)

        # Prepare the MQ client
        self.mq = MQClient(
            broker_hostname=broker_hostname,
            broker_port=broker_port,
            broker_hb_port=broker_hb_port,
            broker_pub_port=broker_pub_port,
            identity=identity,
            topic_prefix=MQ.TOPIC_PREFIX,
            sub_methods={},
        )
        self.mq.connection_changed.connect(self.set_connection_status)
        self.mq.instruments_received.connect(self.update_instruments)
        self.mq.feed_started.connect(self.feed_started)
        self.mq.recent_candles.connect(self.on_recent_candles)

        self.wire_signals()
        self.log.info(QTL.SIGNALS_WIRED)

        # Defer this, give Qt a chance to start the event loop
        QTimer.singleShot(0, self.start_mq)
        self.log.info(QTL.ENABLING_HEARTBEAT)

        # Track the active topic
        self._active_topic: str | None = None
        self._active_instrument: str | None = None

    def clear_data(self) -> None:
        js = "updateCandles([]);"
        self.web_view.page().runJavaScript(js)

    def feed_started(self, feed_data):
        name = feed_data[C_INST.NAME]
        self.ui.lbl_current_pair.setStyleSheet("color: #bbaa66; font-weight bold;")
        self.ui.lbl_current_pair.setText(name)
        self.log.debug(f"Feed Started: {name}")

    def on_candle_received(self, topic: str, candle: dict) -> None:
        if topic != self._active_topic:
            self.log.warning(f"Received off-topic candle: {topic}")
            return

        new_candle = Candle.from_db(candle)
        self.client_db.upsert_candles([new_candle])

        self.log.debug(f"Received: {new_candle}")
        self.render_cached_candles(topic=topic, instrument=new_candle.instrument)

    def on_instrument_changed(self):
        ins_name = self.ui.cb_instrument.currentData()

        if not ins_name:
            self.log.warning("No instrument selected")
            return

        self.clear_data()

        instrument = self._instruments[ins_name]
        display_name = instrument.get(C_INST.DISPLAY_NAME, ins_name)

        self.ui.lbl_current_pair.setText(f"{display_name} - {ins_name}")
        self.log.info(f"Selected instrument: {ins_name}")

        topic = self.mq.candle_topic(ins_name)
        self._active_topic = topic
        self._active_instrument = ins_name

        candles = self.client_db.get_recent_candles(
            name=ins_name,
            limit=DEF.MAX_PLOTLY_CANDLES,
        )
        if candles:
            self.render_candles(topic=topic, candles=candles)
        else:
            self.mq.get_recent_candles(
                topic=topic,
                instrument=instrument,
                count=DEF.MAX_PLOTLY_CANDLES,
            )

        self.mq.register_sub_handler(topic, self.on_candle_received)
        self.mq.subscribe(topic=topic)
        self.mq.start_feed(instrument=instrument)

    def on_recent_candles(self, topic: str, candles: list[dict]) -> None:
        if topic != self._active_topic:
            self.log.warning(f"Received off-topic recent candles: {topic}")
            return

        self.client_db.upsert_candles(candles)

        instrument = self._active_instrument
        if instrument is None:
            return

        recent_candles = self.client_db.get_recent_candles(
            name=instrument,
            limit=DEF.MAX_PLOTLY_CANDLES,
        )
        self.render_candles(topic=topic, candles=recent_candles)

        self.log.debug(f"Recent candles received: {topic}: {len(recent_candles)}")

    def render_candles(self, topic: str, candles: list[Candle]) -> None:
        if not candles:
            return

        recent = list(reversed(candles[-DEF.RECENT_CANDLE_MAX :]))
        self.recent_candles_model.load_data(recent)
        self.resize_recent_candles_columns()

        self.update_plot(topic=topic)

    def render_cached_candles(self, topic: str, instrument: str) -> None:
        candles = self.client_db.get_recent_candles(
            name=instrument,
            limit=DEF.MAX_PLOTLY_CANDLES,
        )
        self.render_candles(topic=topic, candles=candles)

    def set_connection_status(self, connected: bool):

        if connected:
            self.ui.lbl_connection.setStyleSheet("color: #009900; font-weight: bold;")
            self.ui.lbl_connection.setText(QTL.CONNECTED)

            if not self._was_connected:
                self.mq.get_instruments()

        else:
            self.ui.lbl_connection.setStyleSheet("color: #ff5500; font-weight: bold;")
            self.ui.lbl_connection.setText(QTL.DISCONNECTED)

        self._was_connected = connected

    def setup_plot(self):
        plot_layout = QVBoxLayout(self.ui.wgt_plot)
        plot_layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView(self.ui.wgt_plot)

        plot_layout.addWidget(self.web_view)

        html = """
        <html>
        <head>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        </head>
        <body style="margin:0; background-color:#111;">
        <div id="chart" style="width:100%; height:100vh;"></div>

        <script>
            const layout = {
                template: "plotly_dark",
                paper_bgcolor: "#111111",
                plot_bgcolor: "#111111",
                margin: {l: 40, r: 20, t: 20, b: 40},
                xaxis: {
                    rangeslider: {visible: false},
                    gridcolor: "#333333"
                },
                yaxis: {
                    gridcolor: "#333333"
                }
            };

            const data = [{
                type: "candlestick",
                x: [],
                open: [],
                high: [],
                low: [],
                close: [],
                name: "MID"
            }];

            Plotly.newPlot("chart", data, layout, {responsive: true});

            function updateCandles(candles) {
                const x = candles.map(c => c.x);
                const open = candles.map(c => c.open);
                const high = candles.map(c => c.high);
                const low = candles.map(c => c.low);
                const close = candles.map(c => c.close);

                Plotly.react("chart", [{
                    type: "candlestick",
                    x: x,
                    open: open,
                    high: high,
                    low: low,
                    close: close,
                    name: "MID"
                }], layout, {responsive: true});
            }
        </script>
        </body>
        </html>
        """

        self.web_view.setHtml(html)

    def setup_recent_candles_table(self) -> None:
        self.recent_candles_model = RecentCandlesModel()
        self.ui.tbl_recent_candles.setModel(self.recent_candles_model)

        self.ui.tbl_recent_candles.verticalHeader().setVisible(False)
        self.resize_recent_candles_columns()

    def resize_recent_candles_columns(self) -> None:
        table = self.ui.tbl_recent_candles

        table.resizeColumnsToContents()
        for column in range(table.model().columnCount()):
            width = table.columnWidth(column)
            table.setColumnWidth(column, width + RECENT_CANDLES_COLUMN_PADDING)

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
        self.db_mgr.close()
        self.ui.close()
        self.log.info("Clean shutdown")

    def start_mq(self):
        self.mq.start()
        self.log.info(QTL.MQ_CLIENT_STARTED)

    def update_plot(self, topic: str) -> None:
        if self._active_instrument is None:
            candles = []
        else:
            candles = self.client_db.get_recent_candles(
                name=self._active_instrument,
                limit=DEF.MAX_PLOTLY_CANDLES,
            )

        payload = [
            {
                "x": (
                    f"{c.y:04d}-{c.mo:02d}-{c.d:02d} " f"{c.h:02d}:{c.mi:02d}:{c.s:02d}"
                ),
                "open": c.mid_o,
                "high": c.mid_h,
                "low": c.mid_l,
                "close": c.mid_c,
            }
            for c in candles
        ]

        js = f"updateCandles({json.dumps(payload)});"
        self.web_view.page().runJavaScript(js)

    def wire_signals(self):
        # Wire up an exit button
        self.ui.btn_exit.clicked.connect(self.shutdown)
        self.ui.btn_load.clicked.connect(self.on_instrument_changed)

    def update_instruments(self, instruments):
        self.log.info("Instruments updated")

        selected = self.ui.cb_instrument.currentData()

        self._instruments = {
            instrument[C_INST.NAME]: instrument for instrument in instruments
        }

        self.ui.cb_instrument.clear()

        for instrument in instruments:
            name = instrument[C_INST.NAME]
            display_name = instrument.get(C_INST.DISPLAY_NAME, name)

            self.ui.cb_instrument.addItem(
                f"{display_name} - {name}",
                name,
            )

        if selected:
            index = self.ui.cb_instrument.findData(selected)
            if index >= 0:
                self.ui.cb_instrument.setCurrentIndex(index)


def main():
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    widget = ClientQt()
    widget.ui.show()

    app.aboutToQuit.connect(widget.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
