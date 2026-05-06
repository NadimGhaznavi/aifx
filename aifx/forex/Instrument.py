# aifx/forex/Instrument.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import dataclass

from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DDb import DColInstrument as COL

@dataclass(slots=True)
class Instrument:
    name: str
    type: str
    display_name: str
    pip_location: int
    margin_rate: float

    @classmethod
    def from_db(cls, row) -> "Instrument":
        return cls(
            name=row["name"],
            type=row["type"],
            display_name=row["display_name"],
            pip_location=row["pip_location"],
            margin_rate=row["margin_rate"],
        )

    @classmethod
    def from_db(cls, ob):
        return cls(
            name= ob["name"]
        )

    def to_dict(self) -> dict[str, object]:
        return {
            COL.NAME: self.name,
            COL.TYPE: self.type,
            COL.DISPLAY_NAME: self.display_name,
            COL.PIP_LOCATION: self.pip_location,
            COL.MARGIN_RATE: self.margin_rate,
        }
