# tests/unit/test_mqqtbrainclient.py
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

from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQQtBrainClient import MQQtBrainClient


class FakeBrainSocket:
    def __init__(self) -> None:
        self.closed: list[int] = []
        self.connected: list[str] = []
        self.disconnected: list[str] = []
        self.recv_items: list[bytes] = []
        self.sent: list[bytes] = []
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

    def send(self, data: bytes, flags=0) -> None:
        self.sent.append(data)

    def setsockopt(self, option: int, value: bytes) -> None:
        self.socket_options.append((option, value))


class FakeBrainContext:
    def __init__(self) -> None:
        self.destroyed: list[int] = []
        self.sockets: list[FakeBrainSocket] = []

    def destroy(self, linger=0) -> None:
        self.destroyed.append(linger)

    def socket(self, _socket_type) -> FakeBrainSocket:
        socket = FakeBrainSocket()
        self.sockets.append(socket)
        return socket


@pytest.fixture
def qt_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.fixture
def fake_brain_client(monkeypatch, qt_app):
    ctx = FakeBrainContext()
    monkeypatch.setattr("aifx.zmq.MQQtBrainClient.zmq.Context", lambda: ctx)
    client = MQQtBrainClient(
        server_hostname="brain.local",
        server_hb_port=10105,
        identity=MODULE.CLIENT_QT,
    )
    client.log.info = lambda *_args, **_kwargs: None
    return client, ctx


def test_mqqtbrainclient_initializes_heartbeat_socket(fake_brain_client) -> None:
    client, ctx = fake_brain_client

    assert client._hb_address == "tcp://brain.local:10105"
    assert len(ctx.sockets) == 1
    assert ctx.sockets[0].socket_options == [(zmq.IDENTITY, b"ClientQt")]
    assert ctx.sockets[0].connected == ["tcp://brain.local:10105"]


def test_mqqtbrainclient_heartbeat_reply_emits_status(fake_brain_client) -> None:
    client, ctx = fake_brain_client
    received = []
    client.brain_status_changed.connect(
        lambda connected, latency_ms: received.append((connected, latency_ms))
    )

    client._heartbeat_tick()

    reply = MQMsg(
        sender=MODULE.BRAIN,
        target=MODULE.CLIENT_QT,
        method=METHOD.HEARTBEAT_REPLY,
    )
    ctx.sockets[0].recv_items.append(reply.to_json())
    client._poll_heartbeat_reply()

    assert received[-1][0] is True
    assert received[-1][1] is not None
    assert received[-1][1] >= 0.0


def test_mqqtbrainclient_quit_disconnects_and_closes(fake_brain_client) -> None:
    client, ctx = fake_brain_client

    client.start()
    client.quit()

    assert ctx.sockets[0].disconnected == ["tcp://brain.local:10105"]
    assert ctx.sockets[0].closed == [0]
    assert ctx.destroyed == [0]
    assert client._stopped is True
