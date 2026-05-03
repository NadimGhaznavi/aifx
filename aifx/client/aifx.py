# aifx/client/aifx.py

import sys
import random

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go

import pandas as pd

from aifx.util.utils import get_his_data_filename, get_instruments_data_filename
from aifx.constants.DPairs import DPair as PAIR
from aifx.constants.DFrequency import DFrequency as FREQ


class aifx(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.view = QWebEngineView()
        self.layout.addWidget(self.view)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        fig = go.Figure(data=[go.Scatter(y=[random.randint(0, 10) for _ in range(20)])])
        html = fig.to_html(include_plotlyjs="cdn")
        self.view.setHtml(html)


def main():
    app = QtWidgets.QApplication([])
    widget = aifx()
    widget.resize(1400, 600)
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
