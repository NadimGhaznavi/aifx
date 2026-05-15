# tests/unit/test_dbmgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import pytest

from aifx.db.DbMgr import DbMgr
from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DDb import DColInstrument as C_INS


def test_dbmgr_rejects_unknown_db_type() -> None:
    with pytest.raises(ValueError):
        DbMgr(db_type="bogus")


def test_new_cache_db_has_empty_tables(db_mgr) -> None:
    assert db_mgr.num_rows(TABLE.INSTRUMENTS) == 0
    assert db_mgr.num_rows(TABLE.CANDLES) == 0


def test_select_one_returns_none_when_no_rows(db_mgr) -> None:
    row = db_mgr.select_one(TABLE.INSTRUMENTS)

    assert row is None


def test_select_all_returns_empty_list_when_no_rows(db_mgr) -> None:
    rows = db_mgr.select_all(TABLE.INSTRUMENTS)

    assert rows == []


def test_upsert_empty_records_returns_zero(db_mgr) -> None:
    rows = db_mgr.upsert(
        table=TABLE.INSTRUMENTS,
        records=[],
        key_fields=[C_INS.NAME],
    )

    assert rows == 0


def test_upsert_instrument_inserts_row(db_mgr, sample_instrument) -> None:
    rows = db_mgr.upsert(
        table=TABLE.INSTRUMENTS,
        records=[sample_instrument.to_dict()],
        key_fields=[C_INS.NAME],
    )

    assert rows == 1
    assert db_mgr.num_rows(TABLE.INSTRUMENTS) == 1


def test_upsert_instrument_updates_existing_row(db_mgr, sample_instrument) -> None:
    first = sample_instrument.to_dict()
    second = sample_instrument.to_dict()
    second[C_INS.DISPLAY_NAME] = "US Dollar/Canadian Dollar"

    db_mgr.upsert(
        table=TABLE.INSTRUMENTS,
        records=[first],
        key_fields=[C_INS.NAME],
    )

    rows = db_mgr.upsert(
        table=TABLE.INSTRUMENTS,
        records=[second],
        key_fields=[C_INS.NAME],
    )

    row = db_mgr.select_one(
        table=TABLE.INSTRUMENTS,
        where=f"{C_INS.NAME} = ?",
        params=(sample_instrument.name,),
    )

    assert rows == 1
    assert db_mgr.num_rows(TABLE.INSTRUMENTS) == 1
    assert row is not None
    assert row[C_INS.DISPLAY_NAME] == "US Dollar/Canadian Dollar"


def test_is_stale_returns_true_for_empty_instruments_table(db_mgr) -> None:
    assert db_mgr.is_stale(TABLE.INSTRUMENTS) is True


def test_is_stale_rejects_table_without_stale_config(db_mgr) -> None:
    with pytest.raises(ValueError):
        db_mgr.is_stale(TABLE.CANDLES)
