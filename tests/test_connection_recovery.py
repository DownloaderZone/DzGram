import asyncio
from types import SimpleNamespace

import pytest

from pyrogram import raw
from pyrogram.connection import Connection
from pyrogram.connection.transport.tcp.tcp import TCP
from pyrogram.session import Session
import pyrogram.session.session as session_module


def make_session() -> Session:
    client = SimpleNamespace(sleep_threshold=0, name="test", ipv6=False, proxy=None)
    return Session(client, 2, b"k" * 256, False)


class FakeTransport:
    """Transport whose connect() blocks until released."""

    instances = []

    def __init__(self, ipv6, proxy, loop=None):
        self.closed = False
        FakeTransport.instances.append(self)

    async def connect(self, address):
        self.connecting = asyncio.Event()
        self.release = asyncio.Event()
        self.connecting.set()
        await self.release.wait()

    async def send(self, data):
        return None

    async def recv(self, length=0):
        return None

    def close(self):
        self.closed = True


async def wait_for_transport(index: int) -> FakeTransport:
    for _ in range(100):
        if len(FakeTransport.instances) > index:
            transport = FakeTransport.instances[index]
            await transport.connecting.wait()
            return transport
        await asyncio.sleep(0)

    raise AssertionError("transport never started connecting")


@pytest.mark.asyncio
async def test_tcp_send_before_connect_is_oserror():
    transport = TCP(False, None)
    try:
        assert transport.writer is None
        with pytest.raises(OSError):
            await transport.send(b"payload")
    finally:
        transport.close()


@pytest.mark.asyncio
async def test_tcp_send_after_close_is_oserror():
    async def serve(reader, writer):
        await reader.read(1024)
        writer.close()

    server = await asyncio.start_server(serve, "127.0.0.1", 0)
    transport = TCP(False, None)
    try:
        await transport.connect(server.sockets[0].getsockname())
        transport.close()
        with pytest.raises(OSError):
            await transport.send(b"payload")
    finally:
        transport.close()
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_connection_send_on_closed_connection_is_oserror():
    connection = Connection(2, False, False, None, server_address="127.0.0.1", port=443)
    with pytest.raises(OSError):
        await connection.send(b"payload")

    connection.close()
    with pytest.raises(OSError):
        await connection.send(b"payload")
    # Closing twice must stay a no-op.
    connection.close()


@pytest.mark.asyncio
async def test_session_send_on_unconnected_transport_is_oserror():
    # The exact crash seen in production: a session whose connection was
    # replaced mid-restart, so the transport writer was still None. It must
    # surface as a retryable OSError, never AttributeError.
    session = make_session()
    session.is_connected.set()
    session.connection = Connection(
        2, False, False, None, server_address="127.0.0.1", port=443
    )

    with pytest.raises(OSError) as excinfo:
        await session.send(raw.functions.Ping(ping_id=0))

    assert not isinstance(excinfo.value, AttributeError)
    assert session.results == {}


@pytest.mark.asyncio
async def test_session_send_uses_the_connection_it_validated():
    session = make_session()
    session.is_connected.set()
    entered = asyncio.Event()
    release = asyncio.Event()

    class OldConnection:
        async def send(self, payload):
            entered.set()
            await release.wait()
            raise OSError("Connection is closed")

    session.connection = OldConnection()
    task = asyncio.create_task(session.send(raw.functions.Ping(ping_id=0)))
    await entered.wait()

    # A restart published a brand-new, not-yet-connected connection while the
    # request was in flight. The send must not touch it.
    session.connection = SimpleNamespace(protocol=None)
    release.set()

    with pytest.raises(OSError):
        await task


@pytest.mark.asyncio
async def test_invoke_retries_after_transport_failure(monkeypatch):
    session = make_session()
    session.is_connected.set()
    calls = []

    async def send(query, **kwargs):
        calls.append(query)
        if len(calls) == 1:
            raise OSError("Connection is not established")
        return "ok"

    async def restart():
        return None

    monkeypatch.setattr(session, "send", send)
    monkeypatch.setattr(session, "restart", restart)

    assert await session.invoke(raw.functions.Ping(ping_id=0), retries=3) == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_wait_started_never_returns_disconnected(monkeypatch):
    session = make_session()

    async def restart():
        return None

    monkeypatch.setattr(session, "restart", restart)

    with pytest.raises(OSError):
        await session._wait_started()


@pytest.mark.asyncio
async def test_session_stop_drops_the_connection():
    session = make_session()

    class Connection:
        def close(self):
            return None

    session.connection = Connection()
    await session.stop()

    assert session.connection is None


@pytest.mark.asyncio
async def test_connection_publishes_protocol_only_after_connect():
    FakeTransport.instances.clear()
    connection = Connection(2, False, False, None, server_address="127.0.0.1", port=443)
    connection.mode = FakeTransport

    task = asyncio.create_task(connection.connect())
    transport = await wait_for_transport(0)

    # Mid-connect the transport must not be reachable through the connection.
    assert connection.protocol is None
    assert not connection.connected
    with pytest.raises(OSError):
        await connection.send(b"payload")

    transport.release.set()
    await task

    assert connection.protocol is transport
    assert connection.connected


@pytest.mark.asyncio
async def test_reconnect_closes_the_previous_transport():
    FakeTransport.instances.clear()
    connection = Connection(2, False, False, None, server_address="127.0.0.1", port=443)
    connection.mode = FakeTransport

    for index in range(2):
        task = asyncio.create_task(connection.connect())
        transport = await wait_for_transport(index)
        transport.release.set()
        await task

    assert len(FakeTransport.instances) == 2
    assert FakeTransport.instances[0].closed
    assert not FakeTransport.instances[1].closed
    assert connection.protocol is FakeTransport.instances[1]


@pytest.mark.asyncio
async def test_cancelled_connect_closes_the_transport():
    FakeTransport.instances.clear()
    connection = Connection(2, False, False, None, server_address="127.0.0.1", port=443)
    connection.mode = FakeTransport

    task = asyncio.create_task(connection.connect())
    transport = await wait_for_transport(0)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert transport.closed
    assert connection.protocol is None


@pytest.mark.asyncio
async def test_start_closes_a_stale_connection(monkeypatch):
    class FailingConnection:
        def __init__(self, *args, **kwargs):
            self.closed = False

        async def connect(self):
            raise OSError("unreachable")

        def close(self):
            self.closed = True

    monkeypatch.setattr(session_module, "Connection", FailingConnection)

    session = make_session()
    stale = FailingConnection()
    session.connection = stale

    with pytest.raises(OSError):
        await session.start(max_attempts=1)

    assert stale.closed
    assert session.connection is None


@pytest.mark.asyncio
async def test_recv_worker_exits_when_connection_is_gone():
    session = make_session()
    session.connection = None

    await asyncio.wait_for(session.recv_worker(), 1)
