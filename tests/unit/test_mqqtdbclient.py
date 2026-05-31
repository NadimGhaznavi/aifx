# tests/unit/test_mqqtdbclient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import pytest
import zmq
from PySide6.QtCore import QCoreApplication

from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQQtDbClient import MQQtDbClient


class FakeQtSocket:
    def __init__(self) -> None:
        self.closed: list[int] = []
        self.connected: list[str] = []
        self.disconnected: list[str] = []
        self.recv_items: list[bytes] = []
        self.sent: list[tuple[bytes, int | None]] = []
        self.socket_options: list[tuple[int, bytes]] = []

    def close(self, linger=0) -> None:
        self.closed.append(linger)

    def connect(self, address: str) -> None:
        self.connected.append(address)

    def disconnect(self, address: str) -> None:
        self.disconnected.append(address)

    def recv(self, copy=True, flags=0):
        if not self.recv_items:
            raise zmq.Again()
        return self.recv_items.pop(0)

    def send(self, data: bytes, flags=None) -> None:
        self.sent.append((data, flags))

    def setsockopt(self, option: int, value: bytes) -> None:
        self.socket_options.append((option, value))


class FakeQtContext:
    def __init__(self) -> None:
        self.destroyed: list[int] = []
        self.sockets: list[FakeQtSocket] = []

    def destroy(self, linger=0) -> None:
        self.destroyed.append(linger)

    def socket(self, _socket_type) -> FakeQtSocket:
        socket = FakeQtSocket()
        self.sockets.append(socket)
        return socket


@pytest.fixture
def qt_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.fixture
def fake_qt_db_client(monkeypatch, qt_app):
    ctx = FakeQtContext()
    monkeypatch.setattr("aifx.zmq.MQQtDbClient.zmq.Context", lambda: ctx)
    client = MQQtDbClient(
        server_hostname="db.local",
        server_port=10107,
        server_hb_port=10108,
        identity=MODULE.CLIENT_QT,
    )
    client.log.info = lambda *_args, **_kwargs: None
    client.log.warning = lambda *_args, **_kwargs: None
    client.log.critical = lambda *_args, **_kwargs: None
    client.log.debug = lambda *_args, **_kwargs: None
    return client, ctx


def test_mqqtdbclient_initializes_and_connects_control_socket(
    fake_qt_db_client,
) -> None:
    client, ctx = fake_qt_db_client

    assert client._address == "tcp://db.local:10107"
    assert client._hb_address == "tcp://db.local:10108"
    assert len(ctx.sockets) == 2
    assert ctx.sockets[0].socket_options == [(zmq.IDENTITY, b"ClientQt")]
    assert ctx.sockets[1].socket_options == [(zmq.IDENTITY, b"ClientQt")]
    assert ctx.sockets[0].connected == ["tcp://db.local:10107"]
    assert ctx.sockets[1].connected == ["tcp://db.local:10108"]


def test_mqqtdbclient_request_sends_message(fake_qt_db_client) -> None:
    client, ctx = fake_qt_db_client

    sent_ok = client.request(
        method=METHOD.UPSERT,
        payload={"table": TABLE.CANDLES},
    )

    sent = MQMsg.from_json(ctx.sockets[0].sent[0][0])
    assert sent_ok is True
    assert ctx.sockets[0].sent[0][1] == zmq.NOBLOCK
    assert sent.sender == MODULE.CLIENT_QT
    assert sent.target == MODULE.DB_SERVER
    assert sent.method == METHOD.UPSERT
    assert sent.payload == {"table": TABLE.CANDLES}


def test_mqqtdbclient_helpers_send_expected_methods(fake_qt_db_client) -> None:
    client, ctx = fake_qt_db_client

    client.num_rows({"table": TABLE.CANDLES})
    client.select_all({"table": TABLE.CANDLES})
    client.select_one({"table": TABLE.CANDLES})
    client.upsert({"table": TABLE.CANDLES})

    methods = [MQMsg.from_json(data).method for data, _flags in ctx.sockets[0].sent]
    assert methods == [
        METHOD.NUM_ROWS,
        METHOD.SELECT_ALL,
        METHOD.SELECT_ONE,
        METHOD.UPSERT,
    ]


def test_mqqtdbclient_poll_reply_emits_generic_and_specific_signals(
    fake_qt_db_client,
) -> None:
    client, ctx = fake_qt_db_client
    generic_replies: list[tuple[str, dict]] = []
    upsert_replies: list[dict] = []
    reply = MQMsg(
        sender=MODULE.DB_SERVER,
        target=MODULE.CLIENT_QT,
        method=f"{METHOD.UPSERT}_reply",
        payload={"rows": 2},
    )

    client.reply_received.connect(
        lambda method, payload: generic_replies.append((method, payload))
    )
    client.upsert_received.connect(lambda payload: upsert_replies.append(payload))

    client.upsert({"table": TABLE.CANDLES})
    ctx.sockets[0].recv_items.append(reply.to_json())
    client._poll_reply()

    assert generic_replies == [(METHOD.UPSERT, {"rows": 2})]
    assert upsert_replies == [{"rows": 2}]
    assert list(client._pending_requests) == []


def test_mqqtdbclient_heartbeat_reply_emits_db_status_with_latency(
    fake_qt_db_client,
) -> None:
    client, ctx = fake_qt_db_client
    received = []
    client.db_status_changed.connect(
        lambda connected, latency_ms: received.append((connected, latency_ms))
    )

    client._heartbeat_tick()

    reply = MQMsg(
        sender=MODULE.DB_SERVER,
        target=MODULE.CLIENT_QT,
        method=METHOD.HEARTBEAT_REPLY,
    )
    ctx.sockets[1].recv_items.append(reply.to_json())
    client._poll_heartbeat_reply()

    assert received[-1][0] is True
    assert received[-1][1] is not None
    assert received[-1][1] >= 0.0


def test_mqqtdbclient_quit_disconnects_and_closes(fake_qt_db_client) -> None:
    client, ctx = fake_qt_db_client

    client.start()
    client.quit()

    assert ctx.sockets[0].disconnected == ["tcp://db.local:10107"]
    assert ctx.sockets[1].disconnected == ["tcp://db.local:10108"]
    assert ctx.sockets[0].closed == [0]
    assert ctx.sockets[1].closed == [0]
    assert ctx.destroyed == [0]
    assert client._stopped is True
