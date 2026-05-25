# tests/unit/test_mqdbclient.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import asyncio

import pytest
import zmq

from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DMethod import DMethod as METHOD
from aifx.constants.DModule import DModule as MODULE
from aifx.zmq.MQDbClient import MQDbClient
from aifx.zmq.MQMsg import MQMsg


class FakeAsyncSocket:
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

    async def recv(self, copy=True):
        return self.recv_items.pop(0)

    async def send(self, data: bytes) -> None:
        self.sent.append(data)

    def setsockopt(self, option: int, value: bytes) -> None:
        self.socket_options.append((option, value))


class FakeAsyncContext:
    def __init__(self) -> None:
        self.destroyed: list[int] = []
        self.sockets: list[FakeAsyncSocket] = []

    def destroy(self, linger=0) -> None:
        self.destroyed.append(linger)

    def socket(self, _socket_type) -> FakeAsyncSocket:
        socket = FakeAsyncSocket()
        self.sockets.append(socket)
        return socket


@pytest.fixture
def fake_db_client(monkeypatch):
    ctx = FakeAsyncContext()
    monkeypatch.setattr("aifx.zmq.MQDbClient.zmq.asyncio.Context", lambda: ctx)
    client = MQDbClient(
        server_hostname="db.local",
        server_port=10107,
        identity=MODULE.BROKER,
    )
    client.log.info = lambda *_args, **_kwargs: None
    client.log.warning = lambda *_args, **_kwargs: None
    client.log.critical = lambda *_args, **_kwargs: None
    client.log.debug = lambda *_args, **_kwargs: None
    return client, ctx


def test_mqdbclient_initializes_control_socket(fake_db_client) -> None:
    client, ctx = fake_db_client

    assert client._address == "tcp://db.local:10107"
    assert len(ctx.sockets) == 1
    assert ctx.sockets[0].socket_options == [(zmq.IDENTITY, b"Broker")]


def test_mqdbclient_start_connects_control_socket(fake_db_client) -> None:
    async def run() -> None:
        client, ctx = fake_db_client

        await client.start()

        assert ctx.sockets[0].connected == ["tcp://db.local:10107"]
        assert client._started is True

    asyncio.run(run())


def test_mqdbclient_request_sends_message_and_returns_payload(fake_db_client) -> None:
    async def run() -> None:
        client, ctx = fake_db_client
        reply = MQMsg(
            sender=MODULE.DB_SERVER,
            target=MODULE.BROKER,
            method=f"{METHOD.UPSERT}_reply",
            payload={"count": 2},
        )
        ctx.sockets[0].recv_items.append(reply.to_json())

        payload = await client.request(
            method=METHOD.UPSERT,
            payload={"table": TABLE.CANDLES},
        )

        sent = MQMsg.from_json(ctx.sockets[0].sent[0])
        assert sent.sender == MODULE.BROKER
        assert sent.target == MODULE.DB_SERVER
        assert sent.method == METHOD.UPSERT
        assert sent.payload == {"table": TABLE.CANDLES}
        assert payload == {"count": 2}

    asyncio.run(run())


def test_mqdbclient_helpers_send_expected_methods(fake_db_client) -> None:
    async def run() -> None:
        client, ctx = fake_db_client
        for method in [
            METHOD.NUM_ROWS,
            METHOD.SELECT_ALL,
            METHOD.SELECT_ONE,
            METHOD.UPSERT,
        ]:
            reply = MQMsg(
                sender=MODULE.DB_SERVER,
                target=MODULE.BROKER,
                method=f"{method}_reply",
                payload={"ok": True},
            )
            ctx.sockets[0].recv_items.append(reply.to_json())

        await client.num_rows({"table": TABLE.CANDLES})
        await client.select_all({"table": TABLE.CANDLES})
        await client.select_one({"table": TABLE.CANDLES})
        await client.upsert({"table": TABLE.CANDLES})

        methods = [MQMsg.from_json(data).method for data in ctx.sockets[0].sent]
        assert methods == [
            METHOD.NUM_ROWS,
            METHOD.SELECT_ALL,
            METHOD.SELECT_ONE,
            METHOD.UPSERT,
        ]

    asyncio.run(run())


def test_mqdbclient_quit_disconnects_and_closes(fake_db_client) -> None:
    async def run() -> None:
        client, ctx = fake_db_client
        await client.start()

        await client.quit()

        assert ctx.sockets[0].disconnected == ["tcp://db.local:10107"]
        assert ctx.sockets[0].closed == [0]
        assert ctx.destroyed == [0]
        assert client._stopped is True

    asyncio.run(run())
