# aifx/mgr/OandaMgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import requests
import pandas as pd

from aifx.constants.DAccount import DAccount as ACCT
from aifx.constants.DDef import DDef as DDEF
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DCandle import DCandle as CANDLE
from aifx.constants.DPrice import DPrice as PRICE


class OandaMgr:

    def __init__(self):
        self.session = requests.Session()

    def _fetch_instruments(self):
        url = f"{DDEF.OANDA_URL}/{ACCT.ACCOUNTS}/{DDEF.ACCOUNT_ID}/{INS.INSTRUMENTS}"
        response = self.session.get(url, params=None, headers=DDEF.SECURE_HEADER)
        return response.status_code, response.json()

    def get_instruments(self):
        code, data = self.fetch_instruments()
        if code == 200:
            df = pd.DataFrame.from_dict(data[INS.INSTRUMENTS])
            return df[
                [INS.NAME, INS.TYPE, INS.DISPLAY_NAME, INS.PIP_LOC, INS.MARGIN_RATE]
            ]
        else:
            return None

    def fetch_candles(self, pair_name, count, granularity):
        url = f"{DDEF.OANDA_URL}/{INS.INSTRUMENTS}/{pair_name}/{CANDLE.CANDLES}"
        params = dict(count=count, granularity=granularity, price=PRICE.MBA)

        response = self.session.get(url=url, params=params, headers=DDEF.SECURE_HEADER)
        return response.status_code, response.json()


if __name__ == "__main__":
    mgr = OandaMgr()
    # 4 hour intervalus: H4
    # print(api.fetch_candles("EUR_NOK", 50, "H4"))
    # Print the first 5 rows
    df = mgr.get_instruments()
    print(df)
