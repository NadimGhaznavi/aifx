# aifx/aifx.py
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
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from aifx.constants.DDef import DDef as DDEF
from aifx.constants.DDb import DTable, DColInstrument as COL

from aifx.mgr.CacheMgr import CacheMgr


class AiFx(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("AiFx starting up...", flush=True)
        self.cache_mgr = CacheMgr()
        print("CacheMgr created...", flush=True)
        self.load_ui()
        print("UI Loaded...", flush=True)
        self.wire_signals()
        print("Signals wired...", flush=True)
        self.load_instruments()
        print("Instruments loaded...", flush=True)
        print("Houston, we have lift-off!!!", flush=True)

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

    def load_instruments(self):
        ok = self.cache_mgr.ensure_instruments()

        if not ok:
            print("Failed to load instruments", flush=True)
            return

        rows = self.cache_mgr.db_mgr.select_all(
            table=DTable.INSTRUMENTS,
            order_by=COL.NAME,
        )

        combo = self.ui.cb_instrument
        combo.clear()

        for row in rows:
            combo.addItem(row[COL.NAME], row[COL.NAME])

    def wire_signals(self):
        # Wire up an exit button
        self.ui.btn_exit.clicked.connect(self.ui.close)

def main():
    app = QApplication(sys.argv)
    widget = AiFx()
    widget.ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
