# tests/unit/test_oandamgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from unittest.mock import MagicMock

import requests

from aifx.constants.DAccount import DAccountF as ACCTF
from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DCandle import DCandleF as CANDLEF
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DOanda import DOanda as OANDA
from aifx.constants.DPrice import DPrice as PRICE
from aifx.forex.Candle import Candle
from aifx.forex.Instrument import Instrument
from aifx.mgr.OandaMgr import OandaMgr


def _mgr() -> OandaMgr:
    return OandaMgr(publish=lambda _payload: None, log_file=None)


def _response(status_code: int, data: dict) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    return response


def _instrument_payload(name: str = "USD_CAD") -> dict:
    return {
        INS.NAME: name,
        INS.TYPE: "CURRENCY",
        INS.DISPLAY_NAME: name.replace("_", "/"),
        INS.PIP_LOC: -4,
        INS.MARGIN_RATE: "0.02",
    }


def _candle_payload(time: str, complete: bool = True) -> dict:
    return {
        CANDLE.COMPLETE: complete,
        CANDLE.TIME: time,
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


def test_fetch_instruments_returns_status_and_data_on_http_200() -> None:
    published = []
    mgr = OandaMgr(publish=published.append, log_file=None)
    data = {INSF.INSTRUMENTS: [_instrument_payload()]}
    mgr.session.get = MagicMock(return_value=_response(200, data))

    code, result = mgr._fetch_instruments()

    assert code == 200
    assert result == data
    mgr.session.get.assert_called_once_with(
        f"{OANDA.OANDA_URL}/{ACCTF.ACCOUNTS}/{OANDA.ACCOUNT_ID}/{INSF.INSTRUMENTS}",
        params=None,
        headers=OANDA.SECURE_HEADER,
        timeout=OANDA.TIMEOUT,
    )
    assert published
    assert published[-1]["latency_ms"] >= 0.0


def test_fetch_instruments_returns_none_tuple_on_non_200() -> None:
    mgr = _mgr()
    mgr.session.get = MagicMock(return_value=_response(500, {"error": "bad"}))

    assert mgr._fetch_instruments() == (None, None)


def test_fetch_instruments_returns_none_tuple_on_request_exception() -> None:
    mgr = _mgr()
    mgr.session.get = MagicMock(side_effect=requests.RequestException("boom"))

    assert mgr._fetch_instruments() == (None, None)


def test_get_instruments_returns_none_when_fetch_fails() -> None:
    mgr = _mgr()
    mgr._fetch_instruments = MagicMock(return_value=(None, None))

    assert mgr.get_instruments() is None


def test_get_instruments_converts_oanda_payloads_to_instruments() -> None:
    mgr = _mgr()
    mgr._fetch_instruments = MagicMock(
        return_value=(
            200,
            {
                INSF.INSTRUMENTS: [
                    _instrument_payload("USD_CAD"),
                    _instrument_payload("EUR_USD"),
                ]
            },
        )
    )

    instruments = mgr.get_instruments()

    assert instruments == [
        Instrument(
            name="USD_CAD",
            type="CURRENCY",
            display_name="USD/CAD",
            pip_location=-4,
            margin_rate=0.02,
        ),
        Instrument(
            name="EUR_USD",
            type="CURRENCY",
            display_name="EUR/USD",
            pip_location=-4,
            margin_rate=0.02,
        ),
    ]


def test_fetch_candles_passes_request_details_and_returns_response() -> None:
    published = []
    mgr = OandaMgr(publish=published.append, log_file=None)
    data = {CANDLEF.CANDLES: [_candle_payload("2026-05-14T19:30:05.000000000Z")]}
    mgr.session.get = MagicMock(return_value=_response(200, data))

    code, result = mgr._fetch_candles(
        pair_name="USD_CAD",
        count=5,
        granularity=CANDLE.GRAN_S5,
    )

    assert code == 200
    assert result == data
    mgr.session.get.assert_called_once_with(
        url=f"{OANDA.OANDA_URL}/{INSF.INSTRUMENTS}/USD_CAD/{CANDLEF.CANDLES}",
        params={
            "count": 5,
            "granularity": CANDLE.GRAN_S5,
            "price": PRICE.MBA,
        },
        headers=OANDA.SECURE_HEADER,
        timeout=OANDA.TIMEOUT,
    )
    assert published
    assert published[-1]["latency_ms"] >= 0.0


def test_get_candles_returns_none_on_non_200() -> None:
    mgr = _mgr()
    mgr._fetch_candles = MagicMock(return_value=(500, {}))

    assert mgr.get_candles("USD_CAD", count=5, granularity=CANDLE.GRAN_S5) is None


def test_get_candles_converts_only_complete_candles() -> None:
    mgr = _mgr()
    complete = _candle_payload("2026-05-14T19:30:05.000000000Z", complete=True)
    incomplete = _candle_payload("2026-05-14T19:30:10.000000000Z", complete=False)
    mgr._fetch_candles = MagicMock(
        return_value=(200, {CANDLEF.CANDLES: [complete, incomplete]})
    )

    candles = mgr.get_candles("USD_CAD", count=5, granularity=CANDLE.GRAN_S5)

    assert candles == [
        Candle.from_oanda(
            instrument="USD_CAD",
            granularity=CANDLE.GRAN_S5,
            ob=complete,
        )
    ]
