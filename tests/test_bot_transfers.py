import asyncio
import io
from hashlib import md5
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.errors import FloodWait
from pyrogram.methods.rate_limiter import AdaptiveBucket
from pyrogram.session import Session
from tests.test_media import FakeStorage, PART_SIZE, CHUNK_SIZE, make_file_id


@pytest.mark.asyncio
async def test_bot_upload_reuses_download_pool_and_retries_rejected_part():
    client = Client("bot_upload", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    client.storage = FakeStorage()
    shared_pool = []
    requests = []
    leases = []
    inflight = 0
    max_inflight = 0

    class Media:
        async def invoke(self, query, **kwargs):
            nonlocal inflight, max_inflight
            assert kwargs["sleep_threshold"] == 0
            requests.append(query.file_part)
            if len(requests) == 1:
                raise FloodWait(0)
            inflight += 1
            max_inflight = max(max_inflight, inflight)
            try:
                await asyncio.sleep(0.1)
                return True
            finally:
                inflight -= 1

    async def pool(dc_id, count):
        leases.append(count)
        while len(shared_pool) < count:
            shared_pool.append(Media())
        return shared_pool[:count]

    client._get_media_session_pool = pool
    data = b"x" * (4 * PART_SIZE)
    budget = client.read_ahead_slots._value
    result = await client.save_file(io.BytesIO(data))
    assert result.md5_checksum == md5(data).hexdigest()
    assert sorted(requests) == [0, 0, 1, 2, 3]
    assert max_inflight > 1
    await client.save_file(io.BytesIO(b"thumbnail"))
    assert leases == [1, 2, 1]
    assert len(shared_pool) == 2
    assert client.upload_sessions == {}
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_shared_cooldown_blocks_workers_and_recovers(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("pyrogram.methods.rate_limiter.time.monotonic", lambda: clock[0])
    bucket = AdaptiveBucket(32, 300, burst=16)
    bucket.pause(2)
    clock[0] += 0.5
    bucket.on_success()
    assert bucket.available == 0
    waits = []

    async def sleep(seconds):
        waits.append(seconds)
        clock[0] += seconds

    monkeypatch.setattr("pyrogram.methods.rate_limiter.asyncio.sleep", sleep)
    await bucket.acquire()
    assert waits[0] == 1.5
    assert bucket.available >= 0
    assert clock[0] >= 102


@pytest.mark.asyncio
async def test_warm_bot_upload_uses_all_ready_connections_immediately():
    client = Client("warm_pool", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    client.storage = FakeStorage()
    started = set()
    all_started = asyncio.Event()

    class Media:
        def __init__(self, index):
            self.index = index
            self.is_connected = asyncio.Event()
            self.is_connected.set()

        async def invoke(self, query, **kwargs):
            started.add(self.index)
            if len(started) == 4:
                all_started.set()
            await asyncio.wait_for(all_started.wait(), 1)
            return True

    async def unexpected_growth(*args):
        raise AssertionError("A warm, full pool must not wait for pool creation")

    client.media_session_pools[2] = [Media(i) for i in range(4)]
    client._get_media_session_pool = unexpected_growth
    result = await asyncio.wait_for(client.save_file(io.BytesIO(b"x" * (8 * PART_SIZE))), 2)
    assert result.parts == 8
    assert started == {0, 1, 2, 3}
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_bot_upload_starts_before_pool_expansion_and_keeps_all_parts():
    client = Client("bot_startup", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    client.storage = FakeStorage()
    first_part = asyncio.Event()
    expanded = asyncio.Event()
    parts = []
    growth = []

    class Media:
        async def invoke(self, query, **kwargs):
            parts.append(query.file_part)
            first_part.set()
            await asyncio.wait_for(expanded.wait(), 1)
            await asyncio.sleep(0)
            return True

    media = Media()

    async def pool(dc_id, count):
        growth.append(count)
        if count > 1:
            await asyncio.wait_for(first_part.wait(), 1)
            expanded.set()
        return [media] * count

    client._get_media_session_pool = pool
    budget = client.read_ahead_slots._value
    result = await asyncio.wait_for(client.save_file(io.BytesIO(b"x" * (20 * PART_SIZE))), 3)
    assert result.parts == 20
    assert sorted(parts) == list(range(20))
    assert growth == [1, 8]
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_bot_upload_finishes_without_waiting_for_slow_pool_growth():
    client = Client("bot_slow_pool", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    client.storage = FakeStorage()
    growth_started = asyncio.Event()
    growth_cancelled = asyncio.Event()

    class Media:
        async def invoke(self, query, **kwargs):
            await growth_started.wait()
            return True

    async def pool(dc_id, count):
        if count > 1:
            growth_started.set()
            try:
                await asyncio.Event().wait()
            finally:
                growth_cancelled.set()
        return [Media()]

    client._get_media_session_pool = pool
    result = await asyncio.wait_for(client.save_file(io.BytesIO(b"x" * (4 * PART_SIZE))), 1)
    assert result.parts == 4
    assert growth_cancelled.is_set()
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_media_pool_expansion_preserves_ready_connections_on_cancel():
    client = Client("pool_cancel", api_id=1, api_hash="test")
    ready = asyncio.Event()
    slow_started = asyncio.Event()
    calls = []
    cached = SimpleNamespace(is_connected=asyncio.Event(), is_restarting=False, last_used=0)
    cached.is_connected.set()
    client.media_session_pools[2] = [cached]

    async def get_session(*args, **kwargs):
        return SimpleNamespace(auth_key=b"key")

    async def make_session(*args):
        calls.append(True)
        if len(calls) == 1:
            ready.set()
            return cached
        slow_started.set()
        await asyncio.Event().wait()

    client.get_session = get_session
    client._make_media_session = make_session
    task = asyncio.create_task(client._get_media_session_pool(2, 3))
    await ready.wait()
    await slow_started.wait()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert len(client.media_session_pools[2]) == 2
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_bot_prefetch_flood_retries_without_duplicate_downloads(monkeypatch):
    client = Client("bot_download", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    started = asyncio.Event()
    attempts = []
    cooldowns = []
    original_pause = AdaptiveBucket.pause

    def pause(bucket, seconds):
        cooldowns.append(seconds)
        original_pause(bucket, seconds)

    monkeypatch.setattr(AdaptiveBucket, "pause", pause)
    data = b"a" * CHUNK_SIZE + b"b" * CHUNK_SIZE

    class Media(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            if query.offset == 0:
                await asyncio.wait_for(started.wait(), 1)
            else:
                attempts.append(query.offset)
                started.set()
                if len(attempts) == 1:
                    raise FloodWait(0)
            return raw.types.upload.File(
                bytes=data[query.offset:query.offset + query.limit], type=None, mtime=0
            )

    async def session(*args, **kwargs):
        return Media()

    async def pool(*args):
        return [Media()]

    client.get_session = session
    client._get_media_session_pool = pool
    budget = client.read_ahead_slots._value
    result = b"".join([part async for part in client.get_file(make_file_id(), file_size=len(data))])
    assert result == data
    assert attempts == [CHUNK_SIZE, CHUNK_SIZE]
    assert cooldowns == [0]
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_download_first_byte_does_not_wait_for_media_handshake():
    client = Client("first_byte", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    requested = asyncio.Event()
    pool_started = asyncio.Event()
    calls = []
    pool_tasks = []

    class API(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            requested.set()
            return raw.types.upload.File(bytes=b"x" * CHUNK_SIZE, type=None, mtime=0)

    async def get_session(dc_id, is_media=False, **kwargs):
        calls.append(is_media)
        if is_media:
            await asyncio.Event().wait()
        return API()

    async def pool(*args):
        pool_tasks.append(asyncio.current_task())
        pool_started.set()
        await asyncio.Event().wait()

    client.get_session = get_session
    client._get_media_session_pool = pool
    download = client.get_file(make_file_id(), file_size=2 * CHUNK_SIZE)
    first = await asyncio.wait_for(download.__anext__(), 1)
    assert len(first) == CHUNK_SIZE
    assert requested.is_set()
    assert calls == [False]
    await download.aclose()
    for task in pool_tasks:
        task.cancel()
    await asyncio.gather(*pool_tasks, return_exceptions=True)
    client.executor.shutdown(wait=True)
