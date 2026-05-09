# aifx/utilsEventMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0
#

from typing import Any
from dataclasses import dataclass, field

from aifx.constants.DMsg import DMsg as MSG
from aifx.constants.DDef import DDef as DEF


@dataclass(slots=True, frozen=True)
class MQEvent:
    event_type: str
    routing_id: bytes | None = None
    client_id: str | None = None
    payload: Any = None
