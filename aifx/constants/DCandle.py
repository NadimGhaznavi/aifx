# aifx/constants/DCandle.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final

from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DDb import DColCandles as COL


class DCandle:
    CANDLES: Final[str] = "candles"
    COMPLETE: Final[str] = "complete"
    INSTRUMENT = INS.INSTRUMENT
    TIME: Final[str] = "time"
    MID: Final[str] = "mid"
    BID: Final[str] = "bid"
    ASK: Final[str] = "ask"
    O: Final[str] = "o"
    H: Final[str] = "h"
    L: Final[str] = "l"
    C: Final[str] = "c"
    VOLUME = COL.VOLUME
    GRAN_S5: Final[str] = "S5"
