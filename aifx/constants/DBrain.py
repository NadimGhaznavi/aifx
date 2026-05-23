# aifx/constants/DBrain.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final

class DBrainF:
    BRAIN: Final[str] ="brain"
    BRAIN_MQ: Final[str] ="brain-mq"
    BRAIN_MQ_EVENTS: Final[str] ="brain-mq-events"
    BROKER_MQ: Final[str] = "broker-mq"
    BROKER_MQ_EVENTS: Final[str] = "broker-mq-events"
    INITIALIZED: Final[str] = "initialized"
    LOADING: Final[str] = "loading"
    PAUSED: Final[str] = "paused"
    RUNNING: Final[str] = "running"
    STOPPED: Final[str] = "stoppped"
    UNINITIALIZED: Final[str] = "uninitialized"
