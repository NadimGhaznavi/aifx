# aifx/mgr/FeedMgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0


import asyncio

from aifx.constants.DMQ import DMQ as MQ


class FeedMgr:
    def __init__(self, oanda, db_mgr, log):
        self.oanda = oanda
        self.db_mgr = db_mgr
        self.log = log
        self._tasks: dict[str, asyncio.Task] = {}

    def start_feed(self, instrument: dict) -> bool:
        name = instrument["name"]

        if name in self._tasks:
            return False

        self._tasks[name] = asyncio.create_task(
            self._bg_feed(name),
            name=f"feed-{name}",
        )
        return True

    async def _bg_feed(self, name: str) -> None:
        self.log.info(f"Feed started: {name}")

        try:
            while True:
                candles = await asyncio.to_thread(
                    self.oanda.get_candles,
                    name,
                    10,
                    "S5",
                )

                if candles:
                    self.db_mgr.upsert(
                        table="candles",
                        records=candles,
                        key_fields=["instrument", "time"],
                    )

                await asyncio.sleep(MQ.FEED_INTERVAL)

        except asyncio.CancelledError:
            self.log.info(f"Feed stopped: {name}")
            raise
