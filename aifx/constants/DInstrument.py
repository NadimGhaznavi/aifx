# aifx/constants/DInstrument.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0from typing import Final

from typing import Final

from aifx.constants.DField import DField as FIELD


class DInstrument:

    DISPLAY_NAME: Final[str] = "displayName"
    NAME = FIELD.NAME
    INSTRUMENT: Final[str] = "Instrument"
    MARGIN_RATE: Final[str] = "marginRate"
    TYPE = FIELD.TYPE
    PIP_LOC: Final[str] = "pipLocation"
    STARTED = FIELD.STARTED


class DInstrumentF:
    INSTRUMENT: Final[str] = "instrument"
    INSTRUMENTS: Final[str] = "instruments"
    TOPIC: Final[str] = "topic"
