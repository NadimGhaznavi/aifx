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

from aifx.mgr.CacheMgr import CacheMgr


class AiFx(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache_mgr = CacheMgr()
        self.load_ui()
        self.wire_signals()

    def load_ui(self):
        loader = QUiLoader()
        path = Path(__file__).resolve().parent / "form.ui"
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Set the window's title bar
        self.setWindowTitle("AI FX")


    def wire_signals(self):
        # Wire up an exit button
        self.ui.btn_exit.clicked.connect(self.close)

def main():
    app = QApplication(sys.argv)
    widget = AiFx()
    widget.ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
