# aifx/constants/DLogging.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final, Mapping

import logging


class DAiFxLog:
    """
    Logging level constants for HydraLog configuration.

    Defines string constants for different logging levels that map
    to Python's standard logging levels via the LOG_LEVELS dictionary.
    """

    INFO: Final[str] = "info"
    DEBUG: Final[str] = "debug"
    WARNING: Final[str] = "warning"
    ERROR: Final[str] = "error"
    CRITICAL: Final[str] = "critical"


LOG_LEVELS: Mapping[DAiFxLog, int] = {
    DAiFxLog.INFO: logging.INFO,
    DAiFxLog.DEBUG: logging.DEBUG,
    DAiFxLog.WARNING: logging.WARNING,
    DAiFxLog.ERROR: logging.ERROR,
    DAiFxLog.CRITICAL: logging.CRITICAL,
}
