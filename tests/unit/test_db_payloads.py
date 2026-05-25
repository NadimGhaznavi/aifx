# tests/unit/test_db_payloads.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import asdict

from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DDb import DbNumRowsRequest
from aifx.constants.DDb import DbSelectAllRequest
from aifx.constants.DDb import DbSelectOneRequest
from aifx.constants.DDb import DbUpsertRequest


def test_db_num_rows_request_payload() -> None:
    request = DbNumRowsRequest(table=TABLE.CANDLES)

    assert asdict(request) == {"table": TABLE.CANDLES}


def test_db_select_all_request_defaults_are_json_native() -> None:
    request = DbSelectAllRequest(table=TABLE.CANDLES)

    assert asdict(request) == {
        "table": TABLE.CANDLES,
        "where": None,
        "params": [],
        "order_by": None,
        "limit": None,
    }


def test_db_select_one_request_payload() -> None:
    request = DbSelectOneRequest(
        table=TABLE.CANDLES,
        where=f"{C_CAND.INSTRUMENT} = ?",
        params=["USD_CAD"],
        order_by=f"{C_CAND.Y} DESC",
    )

    assert asdict(request) == {
        "table": TABLE.CANDLES,
        "where": "instrument = ?",
        "params": ["USD_CAD"],
        "order_by": "y DESC",
    }


def test_db_upsert_request_payload() -> None:
    record = {
        C_CAND.INSTRUMENT: "USD_CAD",
        C_CAND.GRANULARITY: "S5",
        C_CAND.Y: 2026,
        C_CAND.MO: 5,
        C_CAND.D: 25,
        C_CAND.H: 12,
        C_CAND.MI: 0,
        C_CAND.S: 0,
    }
    key_fields = [
        C_CAND.INSTRUMENT,
        C_CAND.GRANULARITY,
        C_CAND.Y,
        C_CAND.MO,
        C_CAND.D,
        C_CAND.H,
        C_CAND.MI,
        C_CAND.S,
    ]

    request = DbUpsertRequest(
        table=TABLE.CANDLES,
        records=[record],
        key_fields=key_fields,
    )

    assert asdict(request) == {
        "table": TABLE.CANDLES,
        "records": [record],
        "key_fields": key_fields,
    }
