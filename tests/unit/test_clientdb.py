# tests/unit/test_clientdb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import replace

from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DTable as TABLE
from aifx.db.ClientDb import ClientDb


def test_clientdb_get_recent_candles_returns_empty_list_when_empty(db_mgr) -> None:
    client_db = ClientDb(db_mgr=db_mgr)

    assert client_db.get_recent_candles("USD_CAD") == []


def test_clientdb_upsert_candles_accepts_candle_objects(db_mgr, sample_candle) -> None:
    client_db = ClientDb(db_mgr=db_mgr)

    rows = client_db.upsert_candles([sample_candle])

    assert rows == 1
    assert client_db.get_recent_candles("USD_CAD") == [sample_candle]


def test_clientdb_upsert_candles_accepts_dict_records(db_mgr, sample_candle) -> None:
    client_db = ClientDb(db_mgr=db_mgr)

    rows = client_db.upsert_candles([sample_candle.to_dict()])

    assert rows == 1
    assert client_db.get_recent_candles("USD_CAD") == [sample_candle]


def test_clientdb_get_recent_candles_filters_limits_and_returns_oldest_first(
    db_mgr, sample_candle
) -> None:
    client_db = ClientDb(db_mgr=db_mgr)
    first = replace(sample_candle, s=0)
    second = replace(sample_candle, s=5)
    third = replace(sample_candle, s=10)
    other_instrument = replace(sample_candle, instrument="EUR_USD", s=15)

    client_db.upsert_candles([third, other_instrument, first, second])

    assert client_db.get_recent_candles("USD_CAD", limit=2) == [second, third]


def test_clientdb_upsert_candles_updates_existing_row(db_mgr, sample_candle) -> None:
    client_db = ClientDb(db_mgr=db_mgr)
    updated = replace(sample_candle, volume=99, mid_c=1.20015)

    client_db.upsert_candles([sample_candle])
    rows = client_db.upsert_candles([updated])

    candles = client_db.get_recent_candles("USD_CAD")
    assert rows == 1
    assert candles == [updated]


def test_clientdb_upsert_instruments_accepts_instrument_objects(
    db_mgr, sample_instrument
) -> None:
    client_db = ClientDb(db_mgr=db_mgr)

    rows = client_db.upsert_instruments([sample_instrument])

    db_row = db_mgr.select_one(TABLE.INSTRUMENTS)
    assert rows == 1
    assert db_row is not None
    assert db_row[C_INST.NAME] == "USD_CAD"


def test_clientdb_upsert_instruments_accepts_dict_records(
    db_mgr, sample_instrument
) -> None:
    client_db = ClientDb(db_mgr=db_mgr)

    rows = client_db.upsert_instruments([sample_instrument.to_dict()])

    db_row = db_mgr.select_one(TABLE.INSTRUMENTS)
    assert rows == 1
    assert db_row is not None
    assert db_row[C_INST.NAME] == "USD_CAD"
