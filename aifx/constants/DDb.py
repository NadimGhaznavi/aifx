# aifx/constants/DDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final


class DColInstrument:
    NAME: Final[str] = "name"
    TYPE: Final[str] = "type"
    DISPLAY_NAME: Final[str] = "display_name"
    PIP_LOCATION: Final[str] = "pip_location"
    MARGIN_RATE: Final[str] = "margin_rate"
    PUB_PORT: Final[str] = "pub_port"


class DDbF:
    CACHE: Final[str] = "cache"
    MEMORY: Final[str] = ":memory:"


class DTable:
    INSTRUMENTS: Final[str] = "instruments"
