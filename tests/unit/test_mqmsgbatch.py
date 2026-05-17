# tests/unit/test_mqmsgbatch.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
import time

import pytest

from aifx.constants.DMQ import DMQ as MQ
from aifx.zmq.MQMsgBatch import MQMsgBatch


def test_new_batch_starts_empty() -> None:
    batch = MQMsgBatch()

    assert batch.batch_num() == 0
    assert batch.batch_size() == 0
    assert batch.is_empty() is True
    assert batch.has_timed_out(time.monotonic() + MQ.MAX_BATCH_TIME) is False


def test_append_requires_lock() -> None:
    batch = MQMsgBatch()

    with pytest.raises(AssertionError, match="append"):
        batch.append({"message": "one"})


def test_pop_batch_requires_lock() -> None:
    batch = MQMsgBatch()

    with pytest.raises(AssertionError, match="pop_batch"):
        batch.pop_batch()


def test_append_tracks_size_and_timeout() -> None:
    async def run() -> None:
        batch = MQMsgBatch()
        await batch.acquire_lock()
        try:
            batch.append({"message": "one"})
            now = time.monotonic()

            assert batch.batch_size() == 1
            assert batch.is_empty() is False
            assert batch.has_timed_out(now) is False
            assert batch.has_timed_out(now + MQ.MAX_BATCH_TIME + 0.01) is True
        finally:
            batch.release_lock()

    asyncio.run(run())


def test_pop_batch_returns_messages_resets_state_and_increments_batch_num() -> None:
    async def run() -> None:
        batch = MQMsgBatch()
        await batch.acquire_lock()
        try:
            batch.append({"message": "one"})
            batch.append({"message": "two"})

            msgs = batch.pop_batch()

            assert msgs == [{"message": "one"}, {"message": "two"}]
            assert batch.batch_num() == 1
            assert batch.batch_size() == 0
            assert batch.is_empty() is True
            assert batch.has_timed_out(time.monotonic() + MQ.MAX_BATCH_TIME) is False
        finally:
            batch.release_lock()

    asyncio.run(run())


def test_batch_can_be_reused_after_pop() -> None:
    async def run() -> None:
        batch = MQMsgBatch()
        await batch.acquire_lock()
        try:
            batch.append({"message": "one"})
            assert batch.pop_batch() == [{"message": "one"}]

            batch.append({"message": "two"})

            assert batch.pop_batch() == [{"message": "two"}]
            assert batch.batch_num() == 2
        finally:
            batch.release_lock()

    asyncio.run(run())
