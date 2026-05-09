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
    GET_INSTRUMENTS_REPLY: Final[str] = "get_instruments_reply"
    HEARTBEAT: Final[str] = "heartbeat"
    HEARTBEAT_REPLY: Final[str] = "heartbeat_reply"
    PING: Final[str] = "ping"
    PING_REPLY: Final[str] = "pong"
