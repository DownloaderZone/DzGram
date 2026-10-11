import asyncio
import socket
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.connection import Connection
from pyrogram.connection.transport.tcp.tcp import TCP
from pyrogram.session import Session
from tests.test_media import CHUNK_SIZE, make_file_id
from tests.test_media import FakeStorage


@pytest.mark.asyncio
async def test_connection_honors_explicit_endpoint():
    connection = Connection(2, False, False, None, media=True,
                            server_address="127.0.0.2", port=8443)
    assert connection.address == ("127.0.0.2", 8443)


@pytest.mark.asyncio
async def test_media_session_uses_advertised_endpoint_and_shared_authorization(monkeypatch):
    client = Client("endpoint", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    client.sessions[4] = SimpleNamespace(auth_key=b"shared")
    client._dc_config = SimpleNamespace(dc_options=[
        raw.types.DcOption(id=4, ip_address="127.0.0.1", port=443),
        raw.types.DcOption(id=4, ip_address="127.0.0.2", port=8443, media_only=True),
    ])

    class Media:
        MAX_RETRIES = 10

        def __init__(self, *args, **kwargs):
            self.auth_key = args[2]
            self.endpoint = (kwargs["server_address"], kwargs["port"])

        async def start(self, **kwargs):
            pass

    async def unexpected_export(*args, **kwargs):
        raise AssertionError("Media sessions sharing an authorized key must not export authorization again")

    client.invoke = unexpected_export
    monkeypatch.setattr("pyrogram.client.Session", Media)
    session = await client.get_session(4, is_media=True)
    assert session.auth_key == b"shared"
    assert session.endpoint == ("127.0.0.2", 8443)
    assert await client.get_session(4, is_media=True) is session
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_direct_tcp_fragmented_packet():
    payload = b"x" * (1024 * 1024)

    async def serve(reader, writer):
        for start in range(0, len(payload), 16384):
            writer.write(payload[start:start + 16384])
            await writer.drain()
            await asyncio.sleep(0)
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(serve, "127.0.0.1", 0)
    transport = TCP(False, None)
    try:
        await transport.connect(server.sockets[0].getsockname())
        assert transport.socket.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY) == 1
        assert await transport.recv(len(payload)) == payload
        assert await transport.recv(1) is None
    finally:
        transport.close()
        await transport.writer.wait_closed()
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
@pytest.mark.parametrize("delayed_pool", [False, True])
@pytest.mark.parametrize("disk", [False, True])
@pytest.mark.parametrize("bot", [False, True])
async def test_prefetch_overlaps_first_chunk_and_preserves_offsets(delayed_pool, disk, tmp_path, bot):
    client = Client("prefetch", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=bot, is_premium=not bot)
    first_started = asyncio.Event()
    second_started = asyncio.Event()
    first_done = asyncio.Event()
    data = b"a" * CHUNK_SIZE + b"b" * CHUNK_SIZE + b"c" * 19
    requests = []

    class Media(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            requests.append(query.offset)
            if query.offset == 0:
                first_started.set()
                if not delayed_pool:
                    await asyncio.wait_for(second_started.wait(), 1)
                first_done.set()
            else:
                second_started.set()
            return raw.types.upload.File(
                bytes=data[query.offset:query.offset + query.limit], type=None, mtime=0
            )

    media = Media()

    async def get_session(*args, **kwargs):
        return media

    async def get_pool(*args):
        await first_started.wait()
        if delayed_pool:
            await first_done.wait()
            await asyncio.sleep(0)
        return [media]

    client.get_session = get_session
    client._get_media_session_pool = get_pool
    budget = client.read_ahead_slots._value
    if disk:
        with (tmp_path / "download.bin").open("w+b") as output:
            async for _ in client.get_file(make_file_id(), file_size=len(data), _write_file=output):
                pass
        assert (tmp_path / "download.bin").read_bytes() == data
    else:
        result = b"".join([chunk async for chunk in client.get_file(make_file_id(), file_size=len(data))])
        assert result == data
    assert sorted(requests) == [0, CHUNK_SIZE, 2 * CHUNK_SIZE]
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("bot", [False, True])
async def test_prefetch_cancelled_on_early_close(bot):
    client = Client("prefetch_close", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=bot, is_premium=not bot)
    started = asyncio.Event()
    cancelled = asyncio.Event()

    class Media(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            if query.offset == 0:
                await asyncio.wait_for(started.wait(), 1)
                return raw.types.upload.File(bytes=b"x" * CHUNK_SIZE, type=None, mtime=0)
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

    async def get_session(*args, **kwargs):
        return Media()

    async def get_pool(*args):
        return [Media()]

    client.get_session = get_session
    client._get_media_session_pool = get_pool
    budget = client.read_ahead_slots._value
    download = client.get_file(make_file_id(), file_size=2 * CHUNK_SIZE)
    await download.__anext__()
    await download.aclose()
    assert cancelled.is_set()
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)
