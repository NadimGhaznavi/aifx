# tests/unit/test_mqevent.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import FrozenInstanceError

import pytest

from aifx.zmq.MQEvent import MQEvent


def test_mqevent_stores_event_type_and_defaults_optional_fields() -> None:
    event = MQEvent(event_type="client_added")

    assert event.event_type == "client_added"
    assert event.routing_id is None
    assert event.client_id is None
    assert event.payload is None


def test_mqevent_stores_routing_id_client_id_and_payload() -> None:
    payload = {"topic": "candles.USD_CAD"}

    event = MQEvent(
        event_type="client_removed",
        routing_id=b"client-1",
        client_id="client-1",
        payload=payload,
    )

    assert event.event_type == "client_removed"
    assert event.routing_id == b"client-1"
    assert event.client_id == "client-1"
    assert event.payload is payload


def test_mqevent_supports_dataclass_equality() -> None:
    first = MQEvent(event_type="client_added", routing_id=b"client-1")
    second = MQEvent(event_type="client_added", routing_id=b"client-1")

    assert first == second


def test_mqevent_is_frozen() -> None:
    event = MQEvent(event_type="client_added")

    with pytest.raises(FrozenInstanceError):
        event.event_type = "client_removed"
