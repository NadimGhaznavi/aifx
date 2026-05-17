# aifx/forex/RecentCandlesModel.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0
#

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from aifx.forex.Candle import Candle


class RecentCandlesModel(QAbstractTableModel):
    HEADERS = ("Time", "Open", "High", "Low", "Close", "Vol")
    BEARISH_BG = QColor(80, 24, 24)
    BULLISH_BG = QColor(24, 72, 32)

    def __init__(self, candles: list[Candle] | None = None):
        super().__init__()
        self.load_data(candles or [])

    def load_data(self, candles: list[Candle]) -> None:
        self.beginResetModel()
        self.candles = candles
        self.row_count = len(candles)
        self.column_count = len(self.HEADERS)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.row_count

    def columnCount(self, parent=QModelIndex()) -> int:
        return self.column_count

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.HEADERS[section]

        if role == Qt.ItemDataRole.DisplayRole:
            return str(section + 1)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        candle = self.candles[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            values = (
                f"{candle.h:02d}:{candle.mi:02d}:{candle.s:02d}",
                f"{candle.mid_o:.5f}",
                f"{candle.mid_h:.5f}",
                f"{candle.mid_l:.5f}",
                f"{candle.mid_c:.5f}",
                str(candle.volume),
            )
            return values[column]

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        if role == Qt.ItemDataRole.BackgroundRole:
            if candle.mid_c < candle.mid_o:
                return self.BEARISH_BG

            if candle.mid_c > candle.mid_o:
                return self.BULLISH_BG

            return None

        return None

    def clear(self) -> None:
        self.load_data([])
