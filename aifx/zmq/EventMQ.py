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
class EventMsg:
    level: str | None = None
    message: str | None = None
    ev_type: str | None = None
    payload: dict[Any, Any] = field(default_factory=dict)


class EventMQ:

    def __init__(self, client_id: str, pub_func):
        self._client_id = client_id
        self._pub_event = pub_func

    async def publish(self, event: EventMsg):
        msg_dict = {
            MSG.SENDER: self._client_id,
            MSG.LEVEL: event.level,
            MSG.MESSAGE: event.message,
            MSG.MSG_TYPE: event.ev_type,
            MSG.PAYLOAD: event.payload,
        }
        await self._pub_event(msg_dict)
