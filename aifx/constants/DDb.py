# aifx/constants/DDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final

class DDb:
    CACHE: Final[str] = "cache"

class DTable:
    INSTRUMENTS: Final[str] = "instruments"

class DColInstrument:
    NAME: Final[str] = "name"
    TYPE: Final[str] = "type"
    DISPLAY_NAME: Final[str] = "display_name"
    PIP_LOCATION: Final[str] = "pip_location"
    MARGIN_RATE: Final[str] = "margin_rate"
