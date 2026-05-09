# aifx/constants/DMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final


class DMQ:
    CANDLES_TOPIC: Final[str] = "candles_topic"
    HEARTBEAT_INTERVAL: Final[float] = 1.0
    LISTEN_INTERVAL: Final[float] = 1.0
    MAX_BATCH_SIZE: Final[int] = 50
    MAX_BATCH_TIME: Final[float] = 0.25
    PROTOCOL_VERSION: Final[str] = "1.0"
    STALE_CLIENTS_TIMEOUT: Final[float] = 10.0
    TOPIC_PREFIX: Final[str] = "aifx"


class DMQF:
    CONTROL: Final[str] = "control"
    HEARTBEAT: Final[str] = "heartbeat"
    PRUNING: Final[str] = "pruning"
