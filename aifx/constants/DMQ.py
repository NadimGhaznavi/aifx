# aifx/constants/DMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final

from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DMethod import DMethod as METHOD


class DMQ:
    CANDLES_TOPIC: Final[str] = "candles_topic"
    CLIENT_TIMEOUT: Final[int] = 30
    FEED_INTERVAL: Final[int] = 5
    HEARTBEAT_INTERVAL: Final[float] = 1.0
    LISTEN_INTERVAL: Final[float] = 1.0
    MAX_BATCH_SIZE: Final[int] = 50
    MAX_BATCH_TIME: Final[float] = 0.25
    OANDA_STATUS_TOPIC: Final[str] = "status.oanda"
    PROTOCOL_VERSION: Final[str] = "1.0"
    PRUNE_INTERVAL: Final[int] = 5
    TOPIC_PREFIX: Final[str] = "aifx"


class DMQF:
    CLIENT_ADDED: Final[str] = "client_added"
    CLIENT_REMOVED: Final[str] = "client_removed"
    CONTROL: Final[str] = "control"
    HEARTBEAT: Final[str] = "heartbeat"
    INSTRUMENTS = INSF.INSTRUMENTS
    PRUNING: Final[str] = "pruning"
    START_FEED_REPLY: Final[str] = "start_feed_reply"


class DMQEvent:
    CLIENT_ADDED = DMQF.CLIENT_ADDED
    CLIENT_REMOVED = DMQF.CLIENT_REMOVED
    GET_INSTRUMENTS = METHOD.GET_INSTRUMENTS
    START_FEED = METHOD.START_FEED
