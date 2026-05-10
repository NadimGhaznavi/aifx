# aifx/forex/Candle.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import dataclass

from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DDb import DColInstrument as COL
from aifx.constants.DNetwork import DNetwork as NET


@dataclass(slots=True)
class Candle:
    name: str

    @classmethod
    def from_oanda(cls, ob: dict) -> "Candle":
        pass

    @classmethod
    def from_db(cls, ob: dict) -> "Candle":
        pass

    def to_dict(self) -> dict[str, object]:
        pass
