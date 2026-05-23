# aifx/constants/DBrain.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final

from aifx.constants.DField import DField as FIELD
from aifx.constants.DInstrument import DInstrumentF as INSF


class DBrainF:
    BRAIN: Final[str] = "brain"
    BRAIN_MQ: Final[str] = "brain-mq"
    BRAIN_MQ_EVENTS: Final[str] = "brain-mq-events"
    BROKER_MQ: Final[str] = "broker-mq"
    BROKER_MQ_EVENTS: Final[str] = "broker-mq-events"
    INITIALIZED = FIELD.INITIALIZED
    INSTRUMENT = INSF.INSTRUMENT
    LOADING = FIELD.LOADING
    PAUSED = FIELD.PAUSED
    RUNNING = FIELD.RUNNING
    START_TS = FIELD.START_TS
    STOP_TS = FIELD.STOP_TS
    STOPPED = FIELD.STOPPED
    UNINITIALIZED = FIELD.UNINITIALIZED
