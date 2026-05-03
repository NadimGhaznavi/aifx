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
    def from_oanda(cls, ob: dict) -> "Instrument":
        return cls(
            name=ob[INS.NAME],
            type=ob[INS.TYPE],
            display_name=ob[INS.DISPLAY_NAME],
            pip_location=ob[INS.PIP_LOC],
            margin_rate=float(ob[INS.MARGIN_RATE]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            COL.NAME: self.name,
            COL.TYPE: self.type,
            COL.DISPLAY_NAME: self.display_name,
            COL.PIP_LOCATION: self.pip_location,
            COL.MARGIN_RATE: self.margin_rate,
        }
