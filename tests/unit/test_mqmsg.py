# tests/unit/test_mqmsg.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import json

import pytest

from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMsg import DMsg as MSG
from aifx.zmq.MQMsg import MQMsg


def test_mqmsg_stores_fields_and_defaults_payload_to_empty_dict() -> None:
    msg = MQMsg(sender="client", target="broker", method="get_instruments")

    assert msg.sender == "client"
    assert msg.target == "broker"
    assert msg.method == "get_instruments"
    assert msg.payload == {}


def test_mqmsg_properties_can_be_updated() -> None:
    msg = MQMsg(sender="client", target="broker", method="old")

    msg.sender = "server"
    msg.target = "client"
    msg.method = "new"
    msg.payload = {"ok": True}

    assert msg.sender == "server"
    assert msg.target == "client"
    assert msg.method == "new"
    assert msg.payload == {"ok": True}


def test_to_dict_includes_protocol_version() -> None:
    msg = MQMsg(
        sender="client",
        target="broker",
        method="start_feed",
        payload={"name": "USD_CAD"},
    )

    ob = msg.to_dict()

    assert ob[MSG.SENDER] == "client"
    assert ob[MSG.TARGET] == "broker"
    assert ob[MSG.METHOD] == "start_feed"
    assert ob[MSG.PAYLOAD] == {"name": "USD_CAD"}
    assert ob[MSG.PROTOCOL_VERSION] == MQ.PROTOCOL_VERSION


def test_to_json_returns_utf8_json_bytes() -> None:
    msg = MQMsg(sender="client", method="ping", payload={"count": 1})

    json_data = msg.to_json()

    assert isinstance(json_data, bytes)
    assert json.loads(json_data.decode("utf-8")) == msg.to_dict()


def test_from_dict_reconstructs_message() -> None:
    msg = MQMsg.from_dict(
        {
            MSG.SENDER: "client",
            MSG.TARGET: "broker",
            MSG.METHOD: "get_instruments",
            MSG.PAYLOAD: {"limit": 10},
        }
    )

    assert msg.sender == "client"
    assert msg.target == "broker"
    assert msg.method == "get_instruments"
    assert msg.payload == {"limit": 10}


def test_from_dict_defaults_missing_target_to_none() -> None:
    msg = MQMsg.from_dict(
        {
            MSG.SENDER: "client",
            MSG.METHOD: "heartbeat",
            MSG.PAYLOAD: {},
        }
    )

    assert msg.target is None


def test_from_dict_defaults_missing_or_none_payload_to_empty_dict() -> None:
    missing = MQMsg.from_dict(
        {
            MSG.SENDER: "client",
            MSG.METHOD: "heartbeat",
        }
    )
    none_payload = MQMsg.from_dict(
        {
            MSG.SENDER: "client",
            MSG.METHOD: "heartbeat",
            MSG.PAYLOAD: None,
        }
    )

    assert missing.payload == {}
    assert none_payload.payload == {}


def test_from_dict_rejects_non_dict_payload() -> None:
    with pytest.raises(TypeError, match="Payload must be a dict"):
        MQMsg.from_dict(
            {
                MSG.SENDER: "client",
                MSG.METHOD: "heartbeat",
                MSG.PAYLOAD: "bad",
            }
        )


def test_from_json_round_trips_from_to_json() -> None:
    original = MQMsg(
        sender="client",
        target="broker",
        method="get_recent_candles",
        payload={"instrument": "USD_CAD", "limit": 10},
    )

    restored = MQMsg.from_json(original.to_json())

    assert restored.to_dict() == original.to_dict()
