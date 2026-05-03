# aifx/mgr/CacheMgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

# aifx/mgr/CacheMgr.py

from aifx.constants.DDb import DDb, DTable, DColInstrument as COL

from aifx.db.DbMgr import DbMgr
from aifx.mgr.OandaMgr import OandaMgr


class CacheMgr:

    def __init__(self, logfile=None):
        self._logfile = logfile
        self.db_mgr = DbMgr(DDb.CACHE, logfile=logfile)
        self.oanda_mgr = OandaMgr()

    def ensure_instruments(self) -> bool:
        if not self.db_mgr.is_stale(DTable.INSTRUMENTS):
            return True

        return self.refresh_instruments()

    def refresh_instruments(self) -> bool:
        instruments = self.oanda_mgr.get_instruments()

        if instruments is None:
            return False

        records = [
            instrument.to_dict()
            for instrument in instruments
        ]

        self.db_mgr.update(
            table=DTable.INSTRUMENTS,
            records=records,
            key_fields=[COL.NAME],
        )

        return True
