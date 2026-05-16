# aifx/constants/DDef.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0


from typing import Final

from aifx.constants.DLogging import DAiFxLog


class DDef:
    DEFAULT_LOG_LEVEL: Final[str] = DAiFxLog.DEBUG
    VERSION: Final[str] = "0.15.19"
    MAX_PLOTLY_CANDLES: Final[int] = 50
    RECENT_CANDLE_MAX: Final[int] = 6
