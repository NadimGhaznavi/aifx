# aifx/forex/Candle.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DDb import DColCandles as C_CAND


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

    @property
    def candle_key(self) -> str:
        return (
            f"{self.y:04d}"
            f"{self.mo:02d}"
            f"{self.d:02d}"
            f"{self.h:02d}"
            f"{self.mi:02d}"
            f"{self.s:02d}"
        )

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
    def from_db(cls, ob: Mapping[str, Any]) -> "Candle":
        return cls(
            instrument=ob[C_CAND.INSTRUMENT],
            granularity=ob[C_CAND.GRANULARITY],
            y=int(ob[C_CAND.Y]),
            mo=int(ob[C_CAND.MO]),
            d=int(ob[C_CAND.D]),
            h=int(ob[C_CAND.H]),
            mi=int(ob[C_CAND.MI]),
            s=int(ob[C_CAND.S]),
            volume=int(ob[C_CAND.VOLUME]),
            mid_o=float(ob[C_CAND.MID_O]),
            mid_h=float(ob[C_CAND.MID_H]),
            mid_l=float(ob[C_CAND.MID_L]),
            mid_c=float(ob[C_CAND.MID_C]),
            bid_o=float(ob[C_CAND.BID_O]),
            bid_h=float(ob[C_CAND.BID_H]),
            bid_l=float(ob[C_CAND.BID_L]),
            bid_c=float(ob[C_CAND.BID_C]),
            ask_o=float(ob[C_CAND.ASK_O]),
            ask_h=float(ob[C_CAND.ASK_H]),
            ask_l=float(ob[C_CAND.ASK_L]),
            ask_c=float(ob[C_CAND.ASK_C]),
        )

    def __repr__(self) -> str:
        ts = (
            f"{self.y:04d}-{self.mo:02d}-{self.d:02d} "
            f"{self.h:02d}:{self.mi:02d}:{self.s:02d}"
        )
        return f"Candle({self.instrument} candle @ {ts})"

    def to_dict(self) -> dict[str, object]:
        # Do not include the "candle_key" column, it's derived
        return {
            C_CAND.INSTRUMENT: self.instrument,
            C_CAND.GRANULARITY: self.granularity,
            C_CAND.Y: self.y,
            C_CAND.MO: self.mo,
            C_CAND.D: self.d,
            C_CAND.H: self.h,
            C_CAND.MI: self.mi,
            C_CAND.S: self.s,
            C_CAND.VOLUME: self.volume,
            C_CAND.MID_O: self.mid_o,
            C_CAND.MID_H: self.mid_h,
            C_CAND.MID_L: self.mid_l,
            C_CAND.MID_C: self.mid_c,
            C_CAND.BID_O: self.bid_o,
            C_CAND.BID_H: self.bid_h,
            C_CAND.BID_L: self.bid_l,
            C_CAND.BID_C: self.bid_c,
            C_CAND.ASK_O: self.ask_o,
            C_CAND.ASK_H: self.ask_h,
            C_CAND.ASK_L: self.ask_l,
            C_CAND.ASK_C: self.ask_c,
        }
