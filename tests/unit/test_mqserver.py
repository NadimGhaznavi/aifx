# tests/unit/test_mqserver.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio
import json
import time

import pytest
import zmq

from aifx.constants.DMQ import DMQEvent
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.constants.DOanda import DOanda as OANDA
from aifx.zmq.MQMsg import MQMsg
from aifx.zmq.MQServer import MQServer


class FakeAsyncSocket:
    def __init__(self) -> None:
        self.bound: list[str] = []
        self.closed: list[int] = []
        self.linger = None
        self.recv_items: list[bytes] = []
        self.sent: list[bytes] = []
        self.sent_multipart: list[list[bytes]] = []
        self.unbound: list[str] = []

    def bind(self, address: str) -> None:
        self.bound.append(address)

    def close(self, linger=0) -> None:
        self.closed.append(linger)

    async def recv(self, copy=True):
        if not self.recv_items:
            await asyncio.sleep(OANDA.TIMEOUT + 0.01)
        return self.recv_items.pop(0)

    async def send(self, data: bytes) -> None:
        self.sent.append(data)

    async def send_multipart(self, frames: list[bytes]) -> None:
        self.sent_multipart.append(frames)

    def unbind(self, address: str) -> None:
        self.unbound.append(address)


class FakeAsyncContext:
    def __init__(self) -> None:
        self.sockets: list[FakeAsyncSocket] = []

    def socket(self, _socket_type) -> FakeAsyncSocket:
        socket = FakeAsyncSocket()
        self.sockets.append(socket)
        return socket


@pytest.fixture
def fake_server(monkeypatch):
    ctx = FakeAsyncContext()
    monkeypatch.setattr("aifx.zmq.MQServer.zmq.asyncio.Context", lambda: ctx)
    server = MQServer(
        hostname="broker.local",
        port=10101,
        hb_port=10102,
        pub_port=10103,
        identity=MODULE.SERVER_MQ,
        topic_prefix="test",
    )
    server.log.info = lambda *_args, **_kwargs: None
    server.log.critical = lambda *_args, **_kwargs: None
    return server, ctx


def test_mqserver_initializes_addresses_and_sockets(fake_server) -> None:
    server, ctx = fake_server

    assert server._address == "tcp://broker.local:10101"
    assert server._hb_address == "tcp://broker.local:10102"
    assert server._pub_address == "tcp://broker.local:10103"
    assert len(ctx.sockets) == 3
    assert ctx.sockets[2].linger == 0


def test_mqserver_builds_topic(fake_server) -> None:
    server, _ctx = fake_server

    assert server.topic("candles.USD_CAD") == "test.candles.USD_CAD"


def test_mqserver_connected_uses_recent_heartbeat(fake_server) -> None:
    server, _ctx = fake_server

    server._last_heartbeat = time.monotonic()
    assert server.connected() is True

    server._last_heartbeat = time.monotonic() - (int(OANDA.TIMEOUT) + 1)
    assert server.connected() is False


def test_mqserver_publish_sends_topic_and_compact_json(fake_server) -> None:
    async def run() -> None:
        server, ctx = fake_server

        await server.publish("test.candles.USD_CAD", {"price": 1.23})

        assert ctx.sockets[2].sent_multipart == [
            [b"test.candles.USD_CAD", b'{"price":1.23}']
        ]

    asyncio.run(run())


def test_mqserver_send_serializes_message(fake_server) -> None:
    async def run() -> None:
        server, ctx = fake_server
        msg = MQMsg(sender=MODULE.SERVER_MQ, target="client", method=METHOD.PING_REPLY)

        await server.send(msg)

        sent = MQMsg.from_json(ctx.sockets[0].sent[0])
        assert sent.to_dict() == msg.to_dict()

    asyncio.run(run())


def test_mqserver_recv_parses_message(fake_server) -> None:
    async def run() -> None:
        server, ctx = fake_server
        msg = MQMsg(sender="client", target=MODULE.SERVER_MQ, method=METHOD.PING)
        ctx.sockets[0].recv_items.append(msg.to_json())

        result = await server.recv()

        assert result.to_dict() == msg.to_dict()

    asyncio.run(run())


def test_mqserver_register_client_adds_new_client_and_event(fake_server) -> None:
    async def run() -> None:
        server, _ctx = fake_server

        await server._register_client(b"client-1")

        assert b"client-1" in server._clients
        event = server.event_queue.get_nowait()
        assert event.event_type == DMQEvent.CLIENT_ADDED
        assert event.routing_id == b"client-1"

    asyncio.run(run())


def test_mqserver_register_existing_client_updates_without_event(fake_server) -> None:
    async def run() -> None:
        server, _ctx = fake_server

        await server._register_client(b"client-1")
        server.event_queue.get_nowait()
        first_seen = server._clients[b"client-1"]
        await asyncio.sleep(0)
        await server._register_client(b"client-1")

        assert server._clients[b"client-1"] >= first_seen
        assert server.event_queue.empty()

    asyncio.run(run())


def test_mqserver_remove_client_removes_client_and_event(fake_server) -> None:
    async def run() -> None:
        server, _ctx = fake_server

        await server._register_client(b"client-1")
        server.event_queue.get_nowait()
        await server._remove_client(b"client-1")

        assert b"client-1" not in server._clients
        event = server.event_queue.get_nowait()
        assert event.event_type == DMQEvent.CLIENT_REMOVED
        assert event.routing_id == b"client-1"

    asyncio.run(run())


def test_mqserver_quit_returns_when_not_started(fake_server) -> None:
    async def run() -> None:
        server, ctx = fake_server

        await server.quit()

        assert ctx.sockets[0].closed == []
        assert ctx.sockets[1].closed == []
        assert ctx.sockets[2].closed == []

    asyncio.run(run())
