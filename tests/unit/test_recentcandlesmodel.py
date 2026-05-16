# tests/unit/test_recentcandlesmodel.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import pytest
from PySide6.QtCore import QCoreApplication, QModelIndex, Qt

from aifx.forex.RecentCandlesModel import RecentCandlesModel


@pytest.fixture(scope="module")
def qt_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


def test_recent_candles_model_starts_empty(qt_app) -> None:
    model = RecentCandlesModel()

    assert model.rowCount() == 0
    assert model.columnCount() == len(RecentCandlesModel.HEADERS)


def test_recent_candles_model_loads_candles(qt_app, sample_candle) -> None:
    model = RecentCandlesModel()

    model.load_data([sample_candle])

    assert model.rowCount() == 1
    assert model.columnCount() == 6


def test_recent_candles_model_horizontal_headers(qt_app) -> None:
    model = RecentCandlesModel()

    headers = [
        model.headerData(section, Qt.Orientation.Horizontal)
        for section in range(model.columnCount())
    ]

    assert headers == list(RecentCandlesModel.HEADERS)


def test_recent_candles_model_vertical_headers_are_one_based(qt_app, sample_candle) -> None:
    model = RecentCandlesModel([sample_candle])

    assert model.headerData(0, Qt.Orientation.Vertical) == "1"


def test_recent_candles_model_ignores_non_display_header_roles(qt_app) -> None:
    model = RecentCandlesModel()

    assert (
        model.headerData(
            0,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.TextAlignmentRole,
        )
        is None
    )


def test_recent_candles_model_formats_display_values(qt_app, sample_candle) -> None:
    model = RecentCandlesModel([sample_candle])

    values = [
        model.data(model.index(0, column), Qt.ItemDataRole.DisplayRole)
        for column in range(model.columnCount())
    ]

    assert values == [
        "19:30:05",
        "1.10010",
        "1.10020",
        "1.10000",
        "1.10015",
        "42",
    ]


def test_recent_candles_model_aligns_display_values_right(qt_app, sample_candle) -> None:
    model = RecentCandlesModel([sample_candle])

    alignment = model.data(model.index(0, 0), Qt.ItemDataRole.TextAlignmentRole)

    assert alignment == Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


def test_recent_candles_model_returns_none_for_invalid_index(qt_app) -> None:
    model = RecentCandlesModel()

    assert model.data(QModelIndex()) is None


def test_recent_candles_model_returns_none_for_unhandled_data_role(
    qt_app, sample_candle
) -> None:
    model = RecentCandlesModel([sample_candle])

    assert model.data(model.index(0, 0), Qt.ItemDataRole.ToolTipRole) is None


def test_recent_candles_model_clear_removes_rows(qt_app, sample_candle) -> None:
    model = RecentCandlesModel([sample_candle])

    model.clear()

    assert model.rowCount() == 0
    assert model.candles == []
