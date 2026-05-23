# aifx/db/BrainDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0
#

from aifx.constants.DDef import DDef as DEF
from aifx.constants.DModule import DModule as MODULE

from aifx.utils.AiFxLog import AiFxLog

class BrainDb:

    def __init__(self, db_mgr: DbMgr, log_level=DEF.DEFAULT_LOG_LEVEL, log_file=None):
        self.db_mgr = db_mgr
        self.log = AiFxLog(client_id=MODULE.BROKER_DB, log_file=log_file, log_level=log_level)