# aifx/db/BrokerDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0
#

from aifx.constants.DDb import DTable as TABLE

from aifx.db.DbMgr import DbMgr
from aifx.forex.Instrument import Instrument


class BrokerDb:

    def __init__(self, db_mgr: DbMgr):
        self.db_mgr = db_mgr

    def get_instruments(self):
        rows = self.db_mgr.select_all(table=TABLE.INSTRUMENTS, order_by="name")

        if not rows:
            return None

        return [
            Instrument(
                name=row["name"],
                type=row["type"],
                display_name=row["display_name"],
                pip_location=row["pip_location"],
                margin_rate=row["margin_rate"],
            )
            for row in rows
        ]
