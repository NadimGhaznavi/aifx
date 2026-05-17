# aifx/constants/DMethod.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final


class DMethod:

    CANDLES_BATCH: Final[str] = "candles_batch"
    COUNTER: Final[str] = "counter"
    GET_INSTRUMENTS: Final[str] = "get_instruments"
    GET_INSTRUMENTS_REPLY: Final[str] = f"{GET_INSTRUMENTS}_reply"
    GET_RECENT_CANDLES: Final[str] = "get_recent_candles"
    GET_RECENT_CANDLES_REPLY: Final[str] = f"{GET_RECENT_CANDLES}_reply"
    HEARTBEAT: Final[str] = "heartbeat"
    HEARTBEAT_REPLY: Final[str] = f"{HEARTBEAT}_reply"
    PING: Final[str] = "ping"
    PING_REPLY: Final[str] = f"{PING}_reply"
    SHUTDOWN: Final[str] = "shutdown"
    SHUTDOWN_REPLY: Final[str] = f"{SHUTDOWN}_reply"
    START_FEED: Final[str] = "start_feed"
    START_FEED_REPLY: Final[str] = f"{START_FEED}_reply"
