import asyncio
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.errors import FloodWait
from pyrogram.methods.rate_limiter import AdaptiveBucket
from pyrogram.session import Session
from tests.test_media import CHUNK_SIZE, FakeStorage, FakeUploadSession, make_file_id


def test_adaptive_rate_recovers_and_backs_off(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("pyrogram.methods.rate_limiter.time.monotonic", lambda: clock[0])
    bucket = AdaptiveBucket(rate=20, ceiling=21, burst=4, step=1)
    clock[0] += 1
    bucket.on_success()
    assert bucket.rate == 21
    bucket.on_flood()
    assert bucket.rate == pytest.approx(17.85)
    bucket.on_flood()
    assert bucket.rate == pytest.approx(17.85)  # One backoff per flood burst.
    clock[0] += 2
    bucket.on_success()
    assert bucket.rate == pytest.approx(18.85)


@pytest.mark.asyncio
async def test_explicit_zero_threshold_surfaces_flood_wait():
    client = SimpleNamespace(sleep_threshold=10, name="test")
    session = Session(client, 2, b"x" * 256, False, is_media=True)
    session.is_connected.set()

    async def flood(*args, **kwargs):
        raise FloodWait(1)

    session.send = flood
    with pytest.raises(FloodWait):
        await session.invoke(raw.functions.Ping(ping_id=0), sleep_threshold=0)


@pytest.mark.asyncio
async def test_upload_flood_wait_retries_and_releases_budget(monkeypatch):
    client = Client("test_flood", api_id=1, api_hash="test")
    client.storage = FakeStorage()

    class FloodSession(FakeUploadSession):
        async def invoke(self, data, **kwargs):
            if not self.invoked:
                self.invoked.append(data.file_part)
                raise FloodWait(0)
            return await super().invoke(data, **kwargs)

    session = FloodSession()
    client.upload_sessions[2] = [session]
    floods = []
    original = AdaptiveBucket.on_flood

    def record_flood(bucket):
        floods.append(True)
        original(bucket)

    monkeypatch.setattr(AdaptiveBucket, "on_flood", record_flood)
    import io
    budget = client.read_ahead_slots._value
    result = await client.save_file(io.BytesIO(b"test"))
    assert result.parts == 1
    assert session.invoked == [0, 0]
    assert floods == [True]
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("premium", [False, True])
async def test_pooled_download_data_limits_and_cleanup(monkeypatch, premium):
    client = Client("test_pool", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=False, is_premium=premium)
    data = b"a" * CHUNK_SIZE + b"b" * CHUNK_SIZE + b"c" * 123

    class MediaSession(Session):
        def __init__(self):
            self.requests = []

        async def invoke(self, query, **kwargs):
            self.requests.append(query.offset)
            await asyncio.sleep(0)
            return raw.types.upload.File(
                bytes=data[query.offset:query.offset + query.limit], type=None, mtime=0
            )

    main = MediaSession()
    pool = [MediaSession(), MediaSession()]
    pool_sizes = []

    async def get_session(*args, **kwargs):
        return main

    async def get_pool(dc_id, n):
        pool_sizes.append(n)
        return pool[:n]

    client.get_session = get_session
    client._get_media_session_pool = get_pool
    if premium:
        async def unexpected_pacing(*args):
            raise AssertionError("Premium downloads must not wait for pacing tokens")
        monkeypatch.setattr(AdaptiveBucket, "acquire", unexpected_pacing)

    initial_budget = client.read_ahead_slots._value
    chunks = [chunk async for chunk in client.get_file(make_file_id(), file_size=len(data))]
    assert b"".join(chunks) == data
    assert client.read_ahead_slots._value == initial_budget

    pool_sizes.clear()
    chunks = [chunk async for chunk in client.get_file(
        make_file_id(), file_size=len(data), limit=1, offset=1
    )]
    assert b"".join(chunks) == data[CHUNK_SIZE:2 * CHUNK_SIZE]
    assert pool_sizes == []  # A one-chunk read should not create a pool.
    client.executor.shutdown(wait=True)
