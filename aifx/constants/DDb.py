# aifx/constants/DDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final

from aifx.constants.DInstrument import DInstrument as INS


class DColInstrument:
    GRANULARITY: Final[str] = "granularity"
    INSTRUMENT = INS.INSTRUMENT
    NAME: Final[str] = "name"
    TYPE: Final[str] = "type"
    DISPLAY_NAME: Final[str] = "display_name"
    PIP_LOCATION: Final[str] = "pip_location"
    MARGIN_RATE: Final[str] = "margin_rate"
    PUB_PORT: Final[str] = "pub_port"
    VOLUME: Final[str] = "volume"
    MID_O: Final[str] = "mid_o"
    MID_H: Final[str] = "mid_h"
    MID_L: Final[str] = "mid_l"
    MID_C: Final[str] = "mid_c"
    BID_O: Final[str] = "bid_o"
    BID_H: Final[str] = "bid_h"
    BID_L: Final[str] = "bid_l"
    BID_C: Final[str] = "bid_c"
    ASK_O: Final[str] = "ask_o"
    ASK_H: Final[str] = "ask_h"
    ASK_L: Final[str] = "ask_l"
    ASK_C: Final[str] = "ask_c"


class DDbF:
    CACHE: Final[str] = "cache"
    MEMORY: Final[str] = ":memory:"


class DTable:
    CANDLES: Final[str] = "candles"
    INSTRUMENTS: Final[str] = "instruments"
