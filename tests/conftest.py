# tests/conftest.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import pytest

from aifx.forex.Candle import Candle
from aifx.forex.Instrument import Instrument

from aifx.db.DbMgr import DbMgr

from aifx.constants.DDb import DDbF as DBF


@pytest.fixture
def sample_candle() -> Candle:
    return Candle(
        instrument="USD_CAD",
        granularity="S5",
        y=2026,
        mo=5,
        d=14,
        h=19,
        mi=30,
        s=5,
        volume=42,
        mid_o=1.1001,
        mid_h=1.1002,
        mid_l=1.1000,
        mid_c=1.10015,
        bid_o=1.0991,
        bid_h=1.0992,
        bid_l=1.0990,
        bid_c=1.09915,
        ask_o=1.1011,
        ask_h=1.1012,
        ask_l=1.1010,
        ask_c=1.10115,
    )


@pytest.fixture
def sample_instrument() -> Instrument:
    return Instrument(
        name="USD_CAD",
        type="CURRENCY",
        display_name="USD/CAD",
        pip_location=-4,
        margin_rate=0.02,
    )


@pytest.fixture
def db_mgr() -> DbMgr:
    db = DbMgr(db_type=DBF.CACHE)
    return db
