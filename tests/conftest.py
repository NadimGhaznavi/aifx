# tests/conftest.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import importlib.util
import sys
import types
from enum import IntEnum, IntFlag

import pytest

if importlib.util.find_spec("requests") is None:
    requests = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class Response:
        status_code = 200

        def json(self):
            return {}

        def raise_for_status(self) -> None:
            pass

        def iter_lines(self):
            return iter(())

    class Session:
        def get(self, *_args, **_kwargs) -> Response:
            return Response()

    requests.RequestException = RequestException
    requests.Response = Response
    requests.Session = Session
    sys.modules["requests"] = requests

if importlib.util.find_spec("PySide6") is None:
    pyside = types.ModuleType("PySide6")
    qt_core = types.ModuleType("PySide6.QtCore")
    qt_gui = types.ModuleType("PySide6.QtGui")
    qt_ui_tools = types.ModuleType("PySide6.QtUiTools")
    qt_web_engine = types.ModuleType("PySide6.QtWebEngineWidgets")
    qt_widgets = types.ModuleType("PySide6.QtWidgets")

    class _Orientation(IntEnum):
        Horizontal = 1
        Vertical = 2

    class _ItemDataRole(IntEnum):
        DisplayRole = 0
        TextAlignmentRole = 1
        BackgroundRole = 2
        ToolTipRole = 3

    class _AlignmentFlag(IntFlag):
        AlignRight = 1
        AlignVCenter = 2

    class _GlobalColor(IntEnum):
        white = 1
        green = 2

    class Qt:
        Orientation = _Orientation
        ItemDataRole = _ItemDataRole
        AlignmentFlag = _AlignmentFlag
        GlobalColor = _GlobalColor
        AlignCenter = 4

    class QModelIndex:
        def __init__(self, row: int = -1, column: int = -1, valid: bool = False):
            self._row = row
            self._column = column
            self._valid = valid

        def column(self) -> int:
            return self._column

        def isValid(self) -> bool:
            return self._valid

        def row(self) -> int:
            return self._row

    class QAbstractTableModel:
        def __init__(self, *_args, **_kwargs):
            pass

        def beginResetModel(self) -> None:
            pass

        def endResetModel(self) -> None:
            pass

        def index(self, row: int, column: int, *_args, **_kwargs) -> QModelIndex:
            return QModelIndex(row=row, column=column, valid=True)

    class QCoreApplication:
        _instance = None

        def __init__(self, *_args, **_kwargs):
            type(self)._instance = self

        @classmethod
        def instance(cls):
            return cls._instance

    class _SignalInstance:
        def __init__(self):
            self._handlers = []

        def connect(self, handler) -> None:
            self._handlers.append(handler)

        def emit(self, *args, **kwargs) -> None:
            for handler in list(self._handlers):
                handler(*args, **kwargs)

    class Signal:
        def __init__(self, *_args, **_kwargs):
            self._name = ""

        def __set_name__(self, _owner, name: str) -> None:
            self._name = f"_{name}_signal"

        def __get__(self, instance, _owner=None):
            if instance is None:
                return self
            signal = instance.__dict__.get(self._name)
            if signal is None:
                signal = _SignalInstance()
                instance.__dict__[self._name] = signal
            return signal

    class QObject:
        def __init__(self, *_args, **_kwargs):
            pass

    class QTimer:
        def __init__(self, *_args, **_kwargs):
            self.timeout = _SignalInstance()

        def start(self, *_args, **_kwargs) -> None:
            pass

        def stop(self) -> None:
            pass

    class QFile:
        ReadOnly = 0

        def __init__(self, *_args, **_kwargs):
            pass

        def close(self) -> None:
            pass

        def open(self, *_args, **_kwargs) -> bool:
            return True

    class QColor:
        def __init__(self, *args):
            self.args = args

        def __eq__(self, other) -> bool:
            return isinstance(other, QColor) and self.args == other.args

    class QPalette:
        class ColorRole(IntEnum):
            Window = 1
            WindowText = 2
            Base = 3
            AlternateBase = 4
            ToolTipBase = 5
            ToolTipText = 6
            Text = 7
            Button = 8
            ButtonText = 9
            BrightText = 10
            Highlight = 11
            HighlightedText = 12

        def setColor(self, *_args, **_kwargs) -> None:
            pass

    class _Widget:
        def __init__(self, *_args, **_kwargs):
            pass

        def __getattr__(self, _name):
            def _method(*_args, **_kwargs):
                return None

            return _method

    qt_core.QAbstractTableModel = QAbstractTableModel
    qt_core.QCoreApplication = QCoreApplication
    qt_core.QFile = QFile
    qt_core.QModelIndex = QModelIndex
    qt_core.QObject = QObject
    qt_core.QTimer = QTimer
    qt_core.Qt = Qt
    qt_core.Signal = Signal

    qt_gui.QColor = QColor
    qt_gui.QPalette = QPalette

    qt_ui_tools.QUiLoader = _Widget
    qt_web_engine.QWebEngineView = _Widget
    qt_widgets.QApplication = QCoreApplication
    qt_widgets.QVBoxLayout = _Widget
    qt_widgets.QWidget = _Widget

    sys.modules["PySide6"] = pyside
    sys.modules["PySide6.QtCore"] = qt_core
    sys.modules["PySide6.QtGui"] = qt_gui
    sys.modules["PySide6.QtUiTools"] = qt_ui_tools
    sys.modules["PySide6.QtWebEngineWidgets"] = qt_web_engine
    sys.modules["PySide6.QtWidgets"] = qt_widgets

from aifx.constants.DDb import DDbF as DBF
from aifx.db.DbMgr import DbMgr
from aifx.forex.Candle import Candle
from aifx.forex.Instrument import Instrument


@pytest.fixture
def sample_candle() -> Candle:
    return Candle(
        instrument="USD_CAD",
        granularity="S5",
        y=2026,
        mo=5,
        d=14,
        h=19,
        mi=30,
        s=5,
        volume=42,
        mid_o=1.1001,
        mid_h=1.1002,
        mid_l=1.1000,
        mid_c=1.10015,
        bid_o=1.0991,
        bid_h=1.0992,
        bid_l=1.0990,
        bid_c=1.09915,
        ask_o=1.1011,
        ask_h=1.1012,
        ask_l=1.1010,
        ask_c=1.10115,
    )


@pytest.fixture
def sample_instrument() -> Instrument:
    return Instrument(
        name="USD_CAD",
        type="CURRENCY",
        display_name="USD/CAD",
        pip_location=-4,
        margin_rate=0.02,
    )


@pytest.fixture
def db_mgr() -> DbMgr:
    db = DbMgr(db_type=DBF.CACHE)
    return db
