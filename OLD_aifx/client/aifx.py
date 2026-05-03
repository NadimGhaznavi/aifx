# aifx/client/aifx.py

import sys
import random

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QToolButton
from PySide6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go

import pandas as pd

from aifx.util.utils import get_his_data_filename, get_instruments_data_filename
from aifx.constants.DPairs import DPair as PAIR
from aifx.constants.DFrequency import DFrequency as FREQ


class aifx(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        button = QToolButton

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

    @QtCore.Slot()
    def quit(self):
        sys.exit(self.  ())


def main():
    app = QtWidgets.QApplication([])
    widget = aifx()
    widget.resize(1400, 600)
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
