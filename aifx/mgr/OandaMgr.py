# aifx/mgr/OandaMgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import json
import requests
import time

from aifx.constants.DAccount import DAccountF as ACCTF
from aifx.constants.DCandle import DCandle as CANDLE, DCandleF as CANDLEF
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DOanda import DOanda as OANDA
from aifx.constants.DPrice import DPrice as PRICE

from aifx.utils.AiFxLog import AiFxLog
from aifx.forex.Instrument import Instrument
from aifx.forex.Candle import Candle


class OandaMgr:

    def __init__(self, log_level=DEF.DEFAULT_LOG_LEVEL, log_file=None):
        self.log = AiFxLog(
            client_id=MODULE.OANDA_MGR, log_file=log_file, log_level=log_level
        )
        self.session = requests.Session()

    def _fetch_candles(self, pair_name, count, granularity):
        url = f"{OANDA.OANDA_URL}/{INSF.INSTRUMENTS}/{pair_name}/{CANDLEF.CANDLES}"
        params = dict(count=count, granularity=granularity, price=PRICE.MBA)

        response = self.session.get(
            url=url,
            params=params,
            headers=OANDA.SECURE_HEADER,
            timeout=OANDA.TIMEOUT,
        )

        return response.status_code, response.json()

    def _fetch_instruments(self):
        url = (
            f"{OANDA.OANDA_URL}/{ACCTF.ACCOUNTS}/{OANDA.ACCOUNT_ID}/{INSF.INSTRUMENTS}"
        )

        try:
            response = self.session.get(
                url,
                params=None,
                headers=OANDA.SECURE_HEADER,
                timeout=OANDA.TIMEOUT,
            )

            if response.status_code != 200:
                return None, None

            data = response.json()
            return 200, data

        except requests.RequestException:
            return None, None

    def get_instruments(self) -> list[Instrument] | None:
        code, data = self._fetch_instruments()

        if code != 200:
            return None
        return [Instrument.from_oanda(ob) for ob in data[INSF.INSTRUMENTS]]

    def get_candles(self, pair_name, count, granularity):
        code, data = self._fetch_candles(
            pair_name=pair_name, count=count, granularity=granularity
        )

        self.log.debug(
            f"Request: {pair_name}, count: {count}, granularity: {granularity}, return code: {code}"
        )

        if code != 200:
            return None

        return [
            Candle.from_oanda(pair_name, granularity, ob)
            for ob in data[CANDLEF.CANDLES]
            if ob[CANDLE.COMPLETE]
        ]

    def stream_prices(self, instruments: list[str]):
        while True:
            try:
                yield from self._try_stream_prices(instruments)

            except json.JSONDecodeError as e:
                print(f"OANDA JSON decode error: {e}")
                time.sleep(OANDA.RETRY)

            except Exception as e:
                print(f"OANDA stream error: {e}")
                time.sleep(OANDA.RETRY)

    def _try_stream_prices(self, instruments: list[str]):
        url = f"{OANDA.OANDA_STREAMING_URL}/v3/{ACCTF.ACCOUNTS}/{OANDA.ACCOUNT_ID}/pricing/stream"

        response = self.session.get(
            url,
            headers=OANDA.SECURE_HEADER,
            params={INSF.INSTRUMENTS: ",".join(instruments)},
            stream=True,
            timeout=(OANDA.TIMEOUT, None),
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            msg = json.loads(line)

            if msg["type"] == PRICE.PRICE:
                yield msg


if __name__ == "__main__":
    mgr = OandaMgr()
    # 4 hour interval: H4
    # print(api.fetch_candles("EUR_NOK", 50, "H4"))
    # Print fetched instruments
    # instruments = mgr.get_instruments()
    # print(instruments)
    mgr = OandaMgr()

    candles = mgr.get_candles(pair_name="EUR_USD", count=5, granularity="S5")

    for candle in candles:
        print(candle)
