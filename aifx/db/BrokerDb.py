# aifx/db/BrokerDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0
#

from aifx.constants.DDb import (
    DTable as TABLE,
    DColInstrument as C_INST,
    DColCandles as C_CAND,
)
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DModule import DModule as MODULE

from aifx.db.DbMgr import DbMgr
from aifx.forex.Instrument import Instrument
from aifx.forex.Candle import Candle

from aifx.utils.AiFxLog import AiFxLog


class BrokerDb:

    def __init__(self, db_mgr: DbMgr, log_level=DEF.DEFAULT_LOG_LEVEL, log_file=None):
        self.db_mgr = db_mgr
        self.log = AiFxLog(client_id=MODULE.BROKER_DB)

    def get_latest_candle(self, name: str) -> Candle | None:
        row = self.db_mgr.select_one(
            table=TABLE.CANDLES,
            where=f"{C_CAND.INSTRUMENT} = ?",
            params=(name,),
            order_by=f"""
                {C_CAND.Y} DESC,
                {C_CAND.MO} DESC,
                {C_CAND.D} DESC,
                {C_CAND.H} DESC,
                {C_CAND.MI} DESC,
                {C_CAND.S} DESC
            """,
        )

        # self.log.debug(f"Latest candle data: {dict(row)}")

        if row is None:
            return None

        return Candle.from_db(row)

    def get_instruments(self):
        rows = self.db_mgr.select_all(table=TABLE.INSTRUMENTS, order_by="name")

        if not rows:
            return None

        return [
            Instrument(
                name=row[C_INST.NAME],
                type=row[C_INST.TYPE],
                display_name=row[C_INST.DISPLAY_NAME],
                pip_location=row[C_INST.PIP_LOCATION],
                margin_rate=row[C_INST.MARGIN_RATE],
            )
            for row in rows
        ]

    def get_recent_candles(self, name: str, limit: int = 10) -> list[Candle]:
        rows = self.db_mgr.select_all(
            table=TABLE.CANDLES,
            where=f"{C_CAND.INSTRUMENT} = ?",
            params=(name,),
            order_by=f"""
                {C_CAND.Y} DESC,
                {C_CAND.MO} DESC,
                {C_CAND.D} DESC,
                {C_CAND.H} DESC,
                {C_CAND.MI} DESC,
                {C_CAND.S} DESC
            """,
            limit=limit,
        )

        if not rows:
            return []

        candles = [Candle.from_db(row) for row in rows]

        # select newest-first for efficient LIMIT, then publish oldest-first
        return list(reversed(candles))
