# tests/unit/test_instrument.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from aifx.forex.Instrument import Instrument

from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DDb import DColInstrument as COL


def test_to_dict(sample_instrument) -> None:
    ob = sample_instrument.to_dict()

    assert ob[COL.NAME] == "USD_CAD"
    assert ob[COL.TYPE] == "CURRENCY"
    assert ob[COL.DISPLAY_NAME] == "USD/CAD"
    assert ob[COL.PIP_LOCATION] == -4
    assert ob[COL.MARGIN_RATE] == 0.02


def test_from_db_round_trip(sample_instrument) -> None:
    restored = Instrument.from_db(sample_instrument.to_dict())

    assert restored == sample_instrument


def test_from_oanda() -> None:
    ob = {
        INS.NAME: "USD_CAD",
        INS.TYPE: "CURRENCY",
        INS.DISPLAY_NAME: "USD/CAD",
        INS.PIP_LOC: -4,
        INS.MARGIN_RATE: "0.02",
    }

    instrument = Instrument.from_oanda(ob)

    assert instrument.name == "USD_CAD"
    assert instrument.type == "CURRENCY"
    assert instrument.display_name == "USD/CAD"
    assert instrument.pip_location == -4
    assert instrument.margin_rate == 0.02
