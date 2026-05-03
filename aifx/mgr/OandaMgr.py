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

from aifx.constants.DAccount import DAccount as ACCT
from aifx.constants.DDef import DDef as DDEF
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DPrice import DPrice as PRICE

from aifx.forex.Instrument import Instrument

class OandaMgr:

    def __init__(self):
        self.session = requests.Session()

    def _fetch_instruments(self):
        url = f"{DDEF.OANDA_URL}/{ACCT.ACCOUNTS}/{DDEF.ACCOUNT_ID}/{INS.INSTRUMENTS}"

        try:
            response = self.session.get(
                url,
                params=None,
                headers=DDEF.SECURE_HEADER,
                timeout=DDEF.OANDA_TIMEOUT,
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

        return [
            Instrument.from_oanda(ob)
            for ob in data[INS.INSTRUMENTS]
        ]

    def fetch_candles(self, pair_name, count, granularity):
        url = f"{DDEF.OANDA_URL}/{INS.INSTRUMENTS}/{pair_name}/{CANDLE.CANDLES}"
        params = dict(count=count, granularity=granularity, price=PRICE.MBA)

        response = self.session.get(
            url=url,
            params=params,
            headers=DDEF.SECURE_HEADER,
            timeout=DDEF.OANDA_TIMEOUT,
        )

        return response.status_code, response.json()

    def stream_prices(self, instruments: list[str]):
        while True:
            try:
                yield from self._try_stream_prices(instruments)

            except json.JSONDecodeError as e:
                print(f"OANDA JSON decode error: {e}")
                time.sleep(DDEF.OANDA_RETRY)

            except Exception as e:
                print(f"OANDA stream error: {e}")
                time.sleep(DDEF.OANDA_RETRY)

    def _try_stream_prices(self, instruments: list[str]):
        url = f"{DDEF.OANDA_STREAM_URL}/v3/{ACCT.ACCOUNTS}/{DDEF.ACCOUNT_ID}/pricing/stream"

        response = self.session.get(
            url,
            headers=DDEF.SECURE_HEADER,
            params={INS.INSTRUMENTS: ",".join(instruments)},
            stream=True,
            timeout=(DDEF.OANDA_TIMEOUT, None),
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
    instruments = mgr.get_instruments()
    print(instruments)
