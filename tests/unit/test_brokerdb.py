# tests/unit/test_brokerdb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import replace

from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INS
from aifx.constants.DDb import DTable as TABLE
from aifx.db.BrokerDb import BrokerDb
from aifx.forex.Instrument import Instrument


def _insert_candles(db_mgr, candles) -> None:
    db_mgr.upsert(
        table=TABLE.CANDLES,
        records=[candle.to_dict() for candle in candles],
        key_fields=[
            C_CAND.INSTRUMENT,
            C_CAND.GRANULARITY,
            C_CAND.Y,
            C_CAND.MO,
            C_CAND.D,
            C_CAND.H,
            C_CAND.MI,
            C_CAND.S,
        ],
    )


def test_get_instruments_returns_none_when_empty(db_mgr) -> None:
    broker_db = BrokerDb(db_mgr=db_mgr)

    assert broker_db.get_instruments() is None


def test_get_instruments_returns_instruments_sorted_by_name(db_mgr) -> None:
    broker_db = BrokerDb(db_mgr=db_mgr)
    cad = Instrument(
        name="USD_CAD",
        type="CURRENCY",
        display_name="USD/CAD",
        pip_location=-4,
        margin_rate=0.02,
    )
    eur = Instrument(
        name="EUR_USD",
        type="CURRENCY",
        display_name="EUR/USD",
        pip_location=-4,
        margin_rate=0.0333,
    )

    db_mgr.upsert(
        table=TABLE.INSTRUMENTS,
        records=[cad.to_dict(), eur.to_dict()],
        key_fields=[C_INS.NAME],
    )

    instruments = broker_db.get_instruments()

    assert instruments == [eur, cad]


def test_get_latest_candle_returns_none_when_empty(db_mgr) -> None:
    broker_db = BrokerDb(db_mgr=db_mgr)

    assert broker_db.get_latest_candle("USD_CAD") is None


def test_get_latest_candle_returns_newest_candle_for_instrument(
    db_mgr, sample_candle
) -> None:
    broker_db = BrokerDb(db_mgr=db_mgr)
    older = replace(sample_candle, s=0)
    newer = replace(sample_candle, s=10)
    other_instrument = replace(newer, instrument="EUR_USD", s=20)

    _insert_candles(db_mgr, [older, newer, other_instrument])

    latest = broker_db.get_latest_candle("USD_CAD")

    assert latest == newer


def test_get_recent_candles_returns_empty_list_when_empty(db_mgr) -> None:
    broker_db = BrokerDb(db_mgr=db_mgr)

    assert broker_db.get_recent_candles("USD_CAD") == []


def test_get_recent_candles_filters_by_instrument_and_returns_oldest_first(
    db_mgr, sample_candle
) -> None:
    broker_db = BrokerDb(db_mgr=db_mgr)
    first = replace(sample_candle, s=0)
    second = replace(sample_candle, s=5)
    third = replace(sample_candle, s=10)
    other_instrument = replace(sample_candle, instrument="EUR_USD", s=15)

    _insert_candles(db_mgr, [third, other_instrument, first, second])

    candles = broker_db.get_recent_candles("USD_CAD", limit=2)

    assert candles == [second, third]
