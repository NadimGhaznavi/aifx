# aifx/utils/Feed.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import dataclass
import asyncio


@dataclass(slots=True)
class Feed:
    name: str
    oanda_task: asyncio.Task | None = None
    oanda_running: bool = False
    pub_task: asyncio.Task | None = None
    pub_running: bool = False
    last_published_key: str | None = None
