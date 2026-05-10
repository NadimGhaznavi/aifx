# aifx/forex/Candle.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import dataclass

from datetime import datetime

from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DDb import DColCandles as COL


@dataclass(slots=True)
class Candle:
    instrument: str
    granularity: str

    y: int
    mo: int
    d: int
    h: int
    mi: int
    s: int

    volume: int

    mid_o: float
    mid_h: float
    mid_l: float
    mid_c: float

    bid_o: float
    bid_h: float
    bid_l: float
    bid_c: float

    ask_o: float
    ask_h: float
    ask_l: float
    ask_c: float

    @classmethod
    def from_oanda(
        cls,
        instrument: str,
        granularity: str,
        ob: dict,
    ) -> "Candle":
        dt = datetime.fromisoformat(ob[CANDLE.TIME].replace("Z", "+00:00"))

        return cls(
            instrument=instrument,
            granularity=granularity,
            y=dt.year,
            mo=dt.month,
            d=dt.day,
            h=dt.hour,
            mi=dt.minute,
            s=dt.second,
            volume=int(ob[CANDLE.VOLUME]),
            mid_o=float(ob[CANDLE.MID][CANDLE.O]),
            mid_h=float(ob[CANDLE.MID][CANDLE.H]),
            mid_l=float(ob[CANDLE.MID][CANDLE.L]),
            mid_c=float(ob[CANDLE.MID][CANDLE.C]),
            bid_o=float(ob[CANDLE.BID][CANDLE.O]),
            bid_h=float(ob[CANDLE.BID][CANDLE.H]),
            bid_l=float(ob[CANDLE.BID][CANDLE.L]),
            bid_c=float(ob[CANDLE.BID][CANDLE.C]),
            ask_o=float(ob[CANDLE.ASK][CANDLE.O]),
            ask_h=float(ob[CANDLE.ASK][CANDLE.H]),
            ask_l=float(ob[CANDLE.ASK][CANDLE.L]),
            ask_c=float(ob[CANDLE.ASK][CANDLE.C]),
        )

    @classmethod
    def from_db(cls, ob: dict) -> "Candle":
        return cls(
            instrument=ob[COL.INSTRUMENT],
            granularity=ob[COL.GRANULARITY],
            y=int(ob[COL.Y]),
            mo=int(ob[COL.MO]),
            d=int(ob[COL.D]),
            h=int(ob[COL.H]),
            mi=int(ob[COL.MI]),
            s=int(ob[COL.S]),
            volume=int(ob[COL.VOLUME]),
            mid_o=float(ob[COL.MID_O]),
            mid_h=float(ob[COL.MID_H]),
            mid_l=float(ob[COL.MID_L]),
            mid_c=float(ob[COL.MID_C]),
            bid_o=float(ob[COL.BID_O]),
            bid_h=float(ob[COL.BID_H]),
            bid_l=float(ob[COL.BID_L]),
            bid_c=float(ob[COL.BID_C]),
            ask_o=float(ob[COL.ASK_O]),
            ask_h=float(ob[COL.ASK_H]),
            ask_l=float(ob[COL.ASK_L]),
            ask_c=float(ob[COL.ASK_C]),
        )

    def __repr__(self) -> str:
        ts = (
            f"{self.y:04d}-{self.mo:02d}-{self.d:02d} "
            f"{self.h:02d}:{self.mi:02d}:{self.s:02d}"
        )
        return f"Candle({self.instrument} candle @ {ts}"

    def to_dict(self) -> dict[str, object]:
        return {
            COL.INSTRUMENT: self.instrument,
            COL.GRANULARITY: self.granularity,
            COL.Y: self.y,
            COL.MO: self.mo,
            COL.D: self.d,
            COL.H: self.h,
            COL.MI: self.mi,
            COL.S: self.s,
            COL.VOLUME: self.volume,
            COL.MID_O: self.mid_o,
            COL.MID_H: self.mid_h,
            COL.MID_L: self.mid_l,
            COL.MID_C: self.mid_c,
            COL.BID_O: self.bid_o,
            COL.BID_H: self.bid_h,
            COL.BID_L: self.bid_l,
            COL.BID_C: self.bid_c,
            COL.ASK_O: self.ask_o,
            COL.ASK_H: self.ask_h,
            COL.ASK_L: self.ask_l,
            COL.ASK_C: self.ask_c,
        }
