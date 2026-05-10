# aifx/zmq/UtilsMQ.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import json
from zmq.sugar.frame import Frame
import zmq

from aifx.constants.DAiFx import DAiFx as AIFX


class MQUtils:
    @staticmethod
    def decode_json(data: bytes | Frame) -> dict:
        raw = MQUtils.ensure_bytes(data)
        return json.loads(raw.decode(AIFX.UTF_8))

    @staticmethod
    def encode_json(data: str) -> bytes:
        return data.encode(AIFX.UTF_8)

    @staticmethod
    def ensure_bytes(data: bytes | Frame) -> bytes:
        return data.bytes if isinstance(data, Frame) else data

    @staticmethod
    def ignore_zmq_teardown(action, what: str) -> None:
        try:
            action()
        except zmq.ZMQError as e:
            print(f"DEBUG: ignoring {what} during shutdown: {type(e).__name__}: {e}")

    @staticmethod
    def split_router_frames(frames: list[bytes]) -> tuple[bytes, bytes, list[bytes]]:
        if len(frames) < 2:
            raise ValueError(f"Expected >=2 frames, got {len(frames)}")

        routing_id = frames[0]

        if len(frames) >= 3 and frames[1] == b"":
            return routing_id, frames[-1], [routing_id, b""]
        return routing_id, frames[-1], [routing_id]
