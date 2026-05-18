# tests/unit/test_mqclient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import time

import pytest
import zmq
from PySide6.QtCore import QCoreApplication

from aifx.constants.DCandle import DCandleF as CANDLEF
from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DInstrument import DInstrument as INS
from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMQ import DMQF as MQF
from aifx.zmq.MQClient import MQClient
from aifx.zmq.MQMsg import MQMsg


class FakeSocket:
    def __init__(self) -> None:
        self.connected: list[str] = []
        self.closed: list[int] = []
        self.sent: list[bytes] = []
        self.recv_items: list[bytes] = []
        self.recv_multipart_items: list[list[bytes]] = []
        self.socket_options: list[tuple[int, bytes]] = []
        self.string_options: list[tuple[int, str]] = []
        self.send_error = None

    def close(self, linger=0) -> None:
        self.closed.append(linger)

    def connect(self, address: str) -> None:
        self.connected.append(address)

    def recv(self, copy=True, flags=0):
        if not self.recv_items:
            raise zmq.Again()
        return self.recv_items.pop(0)

    def recv_multipart(self, flags=0):
        if not self.recv_multipart_items:
            raise zmq.Again()
        return self.recv_multipart_items.pop(0)

    def send(self, data: bytes, flags=0) -> None:
        if self.send_error is not None:
            raise self.send_error
        self.sent.append(data)

    def setsockopt(self, option: int, value: bytes) -> None:
        self.socket_options.append((option, value))

    def setsockopt_string(self, option: int, value: str) -> None:
        self.string_options.append((option, value))


class FakeContext:
    def __init__(self) -> None:
        self.sockets: list[FakeSocket] = []
        self.destroyed: list[int] = []

    def destroy(self, linger=0) -> None:
        self.destroyed.append(linger)

    def socket(self, _socket_type) -> FakeSocket:
        socket = FakeSocket()
        self.sockets.append(socket)
        return socket


@pytest.fixture(scope="module")
def qt_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.fixture
def fake_client(monkeypatch, qt_app):
    ctx = FakeContext()
    monkeypatch.setattr("aifx.zmq.MQClient.zmq.Context", lambda: ctx)
    client = MQClient(
        broker_hostname="broker.local",
        broker_port=10101,
        broker_hb_port=10102,
        broker_pub_port=10103,
        identity=MODULE.CLIENT_MQ,
        topic_prefix="test",
    )
    client.log.info = lambda *_args, **_kwargs: None
    client.log.warning = lambda *_args, **_kwargs: None
    client.log.critical = lambda *_args, **_kwargs: None
    client.log.debug = lambda *_args, **_kwargs: None
    return client, ctx


def test_mqclient_initializes_sockets_and_addresses(fake_client) -> None:
    client, ctx = fake_client

    assert client._address == "tcp://broker.local:10101"
    assert client._hb_address == "tcp://broker.local:10102"
    assert client._sub_address == "tcp://broker.local:10103"
    assert len(ctx.sockets) == 3
    assert ctx.sockets[0].connected == [client._address]
    assert ctx.sockets[1].connected == [client._hb_address]
    assert ctx.sockets[2].connected == [client._sub_address]
    assert ctx.sockets[0].socket_options == [(zmq.IDENTITY, b"MQClient")]
    assert ctx.sockets[1].socket_options == [(zmq.IDENTITY, b"MQClient")]


def test_mqclient_builds_topics(fake_client) -> None:
    client, _ctx = fake_client

    assert client.topic("candles.USD_CAD") == "test.candles.USD_CAD"
    assert client.candle_topic("USD_CAD") == "test.candles.USD_CAD"


def test_mqclient_connected_uses_recent_heartbeat(fake_client) -> None:
    client, _ctx = fake_client

    client._last_heartbeat = time.monotonic()
    assert client.connected() is True

    client._last_heartbeat = time.monotonic() - (3 * int(MQ.HEARTBEAT_INTERVAL))
    assert client.connected() is False


def test_mqclient_heartbeat_reply_emits_broker_status_with_latency(
    fake_client,
) -> None:
    client, ctx = fake_client
    received = []
    client.broker_status_changed.connect(
        lambda connected, latency_ms: received.append((connected, latency_ms))
    )

    client._heartbeat_tick()

    reply = MQMsg(
        sender=MODULE.BROKER,
        target=MODULE.CLIENT_MQ,
        method=METHOD.HEARTBEAT_REPLY,
    )
    ctx.sockets[1].recv_items.append(reply.to_json())
    client._poll_heartbeat_reply()

    assert received[-1][0] is True
    assert received[-1][1] is not None
    assert received[-1][1] >= 0.0


def test_mqclient_register_subscribe_and_unsubscribe(fake_client) -> None:
    client, ctx = fake_client

    def handler(_topic, _payload):
        pass

    client.register_sub_handler("test.candles.USD_CAD", handler)
    client.subscribe("test.candles.USD_CAD")
    client.unsubscribe("test.candles.USD_CAD")

    assert client._sub_methods["test.candles.USD_CAD"] is handler
    assert ctx.sockets[2].string_options == [
        (zmq.SUBSCRIBE, "test.candles.USD_CAD"),
        (zmq.UNSUBSCRIBE, "test.candles.USD_CAD"),
    ]


def test_mqclient_send_serializes_message(fake_client) -> None:
    client, ctx = fake_client
    msg = MQMsg(sender="client", target="broker", method=METHOD.PING)

    assert client.send(msg) is True
    sent = MQMsg.from_json(ctx.sockets[0].sent[0])
    assert sent.method == METHOD.PING


def test_mqclient_send_returns_false_when_socket_would_block(fake_client) -> None:
    client, ctx = fake_client
    ctx.sockets[0].send_error = zmq.Again()

    msg = MQMsg(sender="client", target="broker", method=METHOD.PING)

    assert client.send(msg) is False


def test_mqclient_get_instruments_sends_request(fake_client) -> None:
    client, ctx = fake_client

    assert client.get_instruments() is True
    msg = MQMsg.from_json(ctx.sockets[0].sent[0])
    assert msg.sender == MODULE.CLIENT_MQ
    assert msg.target == "broker.local"
    assert msg.method == METHOD.GET_INSTRUMENTS
    assert msg.payload == {}


def test_mqclient_get_recent_candles_sends_request(fake_client) -> None:
    client, ctx = fake_client

    assert client.get_recent_candles("topic", {C_INST.NAME: "USD_CAD"}, 5) is True
    msg = MQMsg.from_json(ctx.sockets[0].sent[0])
    assert msg.sender == MODULE.CLIENT_MQ
    assert msg.target == "broker.local"
    assert msg.method == METHOD.GET_RECENT_CANDLES
    assert msg.payload == {
        C_CAND.INSTRUMENT: "USD_CAD",
        DBF.LIMIT: 5,
        INSF.TOPIC: "topic",
    }


def test_mqclient_start_feed_sends_start_feed_message(fake_client) -> None:
    client, ctx = fake_client
    instrument = {INS.NAME: "USD_CAD"}

    assert client.start_feed(instrument) is True
    msg = MQMsg.from_json(ctx.sockets[0].sent[0])
    assert msg.sender == MODULE.CLIENT_MQ
    assert msg.target == MODULE.BROKER
    assert msg.method == METHOD.START_FEED
    assert msg.payload == instrument


def test_mqclient_poll_control_reply_emits_instruments(fake_client) -> None:
    client, ctx = fake_client
    received = []
    client.instruments_received.connect(received.append)
    reply = MQMsg(
        sender=MODULE.BROKER,
        target=MODULE.CLIENT_MQ,
        method=METHOD.GET_INSTRUMENTS_REPLY,
        payload={MQF.INSTRUMENTS: [{"name": "USD_CAD"}]},
    )
    ctx.sockets[0].recv_items.append(reply.to_json())

    client._poll_control_reply()

    assert received == [[{"name": "USD_CAD"}]]


def test_mqclient_poll_control_reply_emits_recent_candles(fake_client) -> None:
    client, ctx = fake_client
    received = []
    client.recent_candles.connect(
        lambda topic, candles: received.append((topic, candles))
    )
    candles = [{C_CAND.INSTRUMENT: "USD_CAD", C_CAND.MID_C: 1.10015}]
    reply = MQMsg(
        sender=MODULE.BROKER,
        target=MODULE.CLIENT_MQ,
        method=METHOD.GET_RECENT_CANDLES_REPLY,
        payload={
            INSF.TOPIC: "test.candles.USD_CAD",
            CANDLEF.CANDLES: candles,
        },
    )
    ctx.sockets[0].recv_items.append(reply.to_json())

    client._poll_control_reply()

    assert received == [("test.candles.USD_CAD", candles)]


def test_mqclient_bg_sub_listen_dispatches_registered_handler(fake_client) -> None:
    client, ctx = fake_client
    received = []
    topic = "test.candles.USD_CAD"
    client.register_sub_handler(topic, lambda t, p: received.append((t, p)))
    ctx.sockets[2].recv_multipart_items.append(
        [topic.encode("utf-8"), b'{"price":1.23}']
    )

    client._bg_sub_listen()

    assert received == [(topic, {"price": 1.23})]


def test_mqclient_quit_closes_sockets_and_context(fake_client) -> None:
    client, ctx = fake_client

    client.quit()

    assert client._stopped is True
    assert client._started is False
    assert ctx.sockets[0].closed == [0]
    assert ctx.sockets[1].closed == [0]
    assert ctx.sockets[2].closed == [0]
    assert ctx.destroyed == [0]
