# tests/unit/test_mqutils.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import pytest
import zmq
from zmq.sugar.frame import Frame

from aifx.zmq.MQUtils import MQUtils


def test_encode_json_encodes_string_as_utf8_bytes() -> None:
    assert MQUtils.encode_json('{"ok": true}') == b'{"ok": true}'


def test_decode_json_decodes_bytes_to_dict() -> None:
    assert MQUtils.decode_json(b'{"ok": true, "count": 2}') == {
        "ok": True,
        "count": 2,
    }


def test_decode_json_decodes_zmq_frame_to_dict() -> None:
    frame = Frame(b'{"topic": "candles.USD_CAD"}')

    assert MQUtils.decode_json(frame) == {"topic": "candles.USD_CAD"}


def test_ensure_bytes_returns_bytes_unchanged() -> None:
    data = b"payload"

    assert MQUtils.ensure_bytes(data) is data


def test_ensure_bytes_returns_frame_bytes() -> None:
    frame = Frame(b"payload")

    assert MQUtils.ensure_bytes(frame) == b"payload"


def test_split_router_frames_without_empty_delimiter() -> None:
    routing_id, payload, reply_prefix = MQUtils.split_router_frames(
        [b"client-1", b"payload"]
    )

    assert routing_id == b"client-1"
    assert payload == b"payload"
    assert reply_prefix == [b"client-1"]


def test_split_router_frames_with_empty_delimiter() -> None:
    routing_id, payload, reply_prefix = MQUtils.split_router_frames(
        [b"client-1", b"", b"payload"]
    )

    assert routing_id == b"client-1"
    assert payload == b"payload"
    assert reply_prefix == [b"client-1", b""]


def test_split_router_frames_rejects_too_few_frames() -> None:
    with pytest.raises(ValueError, match="Expected >=2 frames"):
        MQUtils.split_router_frames([b"client-1"])


def test_ignore_zmq_teardown_suppresses_zmq_error(capsys) -> None:
    def fail() -> None:
        raise zmq.ZMQError("context terminated")

    MQUtils.ignore_zmq_teardown(fail, "socket close")

    assert "DEBUG: ignoring socket close during shutdown" in capsys.readouterr().out


def test_ignore_zmq_teardown_does_not_suppress_other_errors() -> None:
    def fail() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        MQUtils.ignore_zmq_teardown(fail, "socket close")
