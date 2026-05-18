# aifx/db/ClientDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0
#

from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DModule import DModule as MODULE
from aifx.db.DbMgr import DbMgr
from aifx.forex.Candle import Candle
from aifx.forex.Instrument import Instrument
from aifx.utils.AiFxLog import AiFxLog


class ClientDb:

    def __init__(self, db_mgr: DbMgr, log_level=DEF.DEFAULT_LOG_LEVEL, log_file=None):
        self.db_mgr = db_mgr
        self.log = AiFxLog(
            client_id=MODULE.CLIENT_DB, log_level=log_level, log_file=log_file
        )

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

        candles = [Candle.from_db(dict(row)) for row in rows]

        return list(reversed(candles))

    def upsert_candles(self, candles: list[Candle] | list[dict]) -> int:
        records = [
            candle.to_dict() if isinstance(candle, Candle) else candle
            for candle in candles
        ]

        return self.db_mgr.upsert(
            table=TABLE.CANDLES,
            records=records,
            key_fields=[
                C_CAND.INSTRUMENT,
                C_CAND.GRANULARITY,
                C_CAND.Y,
                C_CAND.MO,
                C_CAND.D,
                C_CAND.H,
                C_CAND.MI,
                C_CAND.S,
            ],
        )

    def upsert_instruments(self, instruments: list[Instrument] | list[dict]) -> int:
        records = [
            instrument.to_dict() if isinstance(instrument, Instrument) else instrument
            for instrument in instruments
        ]

        return self.db_mgr.upsert(
            table=TABLE.INSTRUMENTS,
            records=records,
            key_fields=[C_INST.NAME],
        )
