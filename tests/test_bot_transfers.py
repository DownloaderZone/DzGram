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
    assert leases == [2, 1]
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
