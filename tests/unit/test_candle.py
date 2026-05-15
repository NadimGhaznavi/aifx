# tests/unit/test_candle.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from aifx.forex.Candle import Candle
from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DDb import DColCandles as C_CAND


def test_candle_key_is_sortable_timestamp_string(sample_candle) -> None:
    assert sample_candle.candle_key == "20260514193005"


def test_to_dict_does_not_include_candle_key(sample_candle) -> None:
    ob = sample_candle.to_dict()

    assert "candle_key" not in ob
    assert ob[C_CAND.INSTRUMENT] == "USD_CAD"
    assert ob[C_CAND.GRANULARITY] == "S5"
    assert ob[C_CAND.Y] == 2026
    assert ob[C_CAND.MO] == 5
    assert ob[C_CAND.D] == 14
    assert ob[C_CAND.H] == 19
    assert ob[C_CAND.MI] == 30
    assert ob[C_CAND.S] == 5
    assert ob[C_CAND.VOLUME] == 42
    assert ob[C_CAND.MID_C] == 1.10015
    assert ob[C_CAND.BID_C] == 1.09915
    assert ob[C_CAND.ASK_C] == 1.10115


def test_from_db_round_trips_from_to_dict(sample_candle) -> None:
    restored = Candle.from_db(sample_candle.to_dict())

    assert restored == sample_candle
    assert restored.candle_key == sample_candle.candle_key


def test_from_oanda_builds_candle() -> None:
    ob = {
        CANDLE.TIME: "2026-05-14T19:30:05.000000000Z",
        CANDLE.VOLUME: 42,
        CANDLE.MID: {
            CANDLE.O: "1.1001",
            CANDLE.H: "1.1002",
            CANDLE.L: "1.1000",
            CANDLE.C: "1.10015",
        },
        CANDLE.BID: {
            CANDLE.O: "1.0991",
            CANDLE.H: "1.0992",
            CANDLE.L: "1.0990",
            CANDLE.C: "1.09915",
        },
        CANDLE.ASK: {
            CANDLE.O: "1.1011",
            CANDLE.H: "1.1012",
            CANDLE.L: "1.1010",
            CANDLE.C: "1.10115",
        },
    }

    candle = Candle.from_oanda(
        instrument="USD_CAD",
        granularity="S5",
        ob=ob,
    )

    assert candle.instrument == "USD_CAD"
    assert candle.granularity == "S5"
    assert candle.candle_key == "20260514193005"
    assert candle.volume == 42
    assert candle.mid_c == 1.10015
    assert candle.bid_c == 1.09915
    assert candle.ask_c == 1.10115
