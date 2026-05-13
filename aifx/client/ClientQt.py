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
from collections import deque
import json

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout

import plotly.graph_objects as go

from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DNetwork import DNetwork as NET
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DQt import DQtL as QTL

from aifx.utils.AiFxLog import AiFxLog
from aifx.zmq.MQClient import MQClient
from aifx.forex.Candle import Candle

# Number of candles to cache for Plotly
MAX_PLOTLY_CANDLES = 50


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

        # Load the UI
        self.load_ui()
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

        self.wire_signals()
        self.log.info(QTL.SIGNALS_WIRED)

        # Defer this, give Qt a chance to start the event loop
        QTimer.singleShot(0, self.start_mq)
        self.log.info(QTL.ENABLING_HEARTBEAT)

        # Store candlestick data here
        self._candles = {}

        # Track the active topic
        self._active_topic: str | None = None

    def clear_data(self) -> None:
        self._candles.clear()

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

        if topic not in self._candles:
            self._candles[topic] = deque(maxlen=MAX_PLOTLY_CANDLES)

        candles = self._candles[topic]

        new_candle = Candle.from_db(candle)
        if not candles:
            candles.append(new_candle)
            self.log.debug(f"First candle received: {topic}: {new_candle}")
            return

        if candles[-1].candle_key == new_candle.candle_key:
            candles[-1] = new_candle
            self.log.warning(f"Duplicate candle: {new_candle}")
        else:
            candles.append(new_candle)

        self.log.debug(f"Received: {new_candle}")

        self.update_plot(topic=topic)

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

        self.mq.get_recent_candles(
            topic=topic,
            instrument=instrument,
            count=MAX_PLOTLY_CANDLES,
        )

        self.mq.register_sub_handler(topic, self.on_candle_received)
        self.mq.subscribe(topic=topic)
        self.mq.start_feed(instrument=instrument)

    def render_candles(self, topic: str) -> None:
        candles = list(self._candles.get(topic, []))

        if not candles:
            return

        x = [
            f"{c.y:04d}-{c.mo:02d}-{c.d:02d} " f"{c.h:02d}:{c.mi:02d}:{c.s:02d}"
            for c in candles
        ]

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=x,
                    open=[c.mid_o for c in candles],
                    high=[c.mid_h for c in candles],
                    low=[c.mid_l for c in candles],
                    close=[c.mid_c for c in candles],
                    name="MID",
                )
            ],
        )

        fig.update_layout(
            title=topic,
            xaxis_title="Time",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            margin=dict(l=30, r=30, t=40, b=30),
            template="plotly_dark",
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        self.web_view.setHtml(html)

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

    def update_plot(self, topic: str) -> None:
        candles = list(self._candles.get(topic, []))

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


def main():
    app = QApplication(sys.argv)

    widget = ClientQt()
    widget.ui.show()

    app.aboutToQuit.connect(widget.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
