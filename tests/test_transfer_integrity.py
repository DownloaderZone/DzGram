import asyncio
import io
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.session import Session
from tests.test_media import FakeStorage, FakeMediaSession, PART_SIZE, CHUNK_SIZE, make_file_id


@pytest.mark.asyncio
async def test_failed_upload_does_not_report_completion():
    client = Client("failed", api_id=1, api_hash="test")
    client.storage = FakeStorage()

    class Failed:
        async def invoke(self, *args, **kwargs):
            raise OSError("failed")

    client.upload_sessions[2] = [Failed()]
    reports = []
    with pytest.raises(OSError):
        await client.save_file(io.BytesIO(b"x"), progress=lambda current, total: reports.append(current))
    assert 1 not in reports
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_upload_cancel_releases_budget_without_draining_queue():
    client = Client("cancel", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    started = asyncio.Event()
    cancelled = asyncio.Event()

    class Blocked:
        async def invoke(self, *args, **kwargs):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

    client.upload_sessions[2] = [Blocked()]
    budget = client.read_ahead_slots._value
    task = asyncio.create_task(client.save_file(io.BytesIO(b"x" * (2 * PART_SIZE))))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 1)
    assert cancelled.is_set()
    assert client.read_ahead_slots._value == budget
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_missing_upload_part_sends_only_requested_part():
    client = Client("repair", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    parts = []

    class Media:
        async def invoke(self, query, **kwargs):
            parts.append((query.file_part, query.bytes))
            return True

    client.upload_sessions[2] = [Media()]
    result = await client.save_file(io.BytesIO(b"a" * PART_SIZE + b"b" * PART_SIZE), file_id=123, file_part=1)
    assert result is None
    assert parts == [(1, b"b" * PART_SIZE)]
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("in_memory", [False, True])
async def test_short_download_fails_and_removes_incomplete_file(tmp_path, in_memory):
    client = Client("short", api_id=1, api_hash="test")
    client.media_sessions[2] = FakeMediaSession(b"short")
    result = await client.handle_download((make_file_id(), str(tmp_path), "test.bin", in_memory,
                                           CHUNK_SIZE, None, ()))
    assert result is None
    assert not (tmp_path / "test.bin").exists()
    assert not (tmp_path / "test.bin.temp").exists()
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_stream_offset_ends_at_actual_file_end():
    client = Client("offset", api_id=1, api_hash="test")
    media = FakeMediaSession(b"a" * CHUNK_SIZE + b"b" * 19)
    client.media_sessions[2] = media
    result = b"".join([chunk async for chunk in client.get_file(
        make_file_id(), file_size=len(media.data), offset=1
    )])
    assert result == b"b" * 19
    media.requests.clear()
    assert [chunk async for chunk in client.get_file(make_file_id(), file_size=len(media.data), offset=2)] == []
    assert media.requests == []
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_short_parallel_download_reports_actual_bytes():
    client = Client("parallel_short", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)

    class Media(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            return raw.types.upload.File(bytes=b"x" * CHUNK_SIZE if query.offset == 0 else b"", type=None, mtime=0)

    async def session(*args, **kwargs):
        return Media()

    async def pool(*args):
        return [Media()]

    client.get_session = session
    client._get_media_session_pool = pool
    reports = []
    chunks = [chunk async for chunk in client.get_file(make_file_id(), file_size=2 * CHUNK_SIZE,
                                                      progress=lambda current, total: reports.append(current))]
    assert len(b"".join(chunks)) == CHUNK_SIZE
    assert max(reports) == CHUNK_SIZE
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_shutdown_cancels_pool_builders_before_closing_sessions():
    client = Client("shutdown", api_id=1, api_hash="test")
    client.is_initialized = True
    started = asyncio.Event()
    cancelled = asyncio.Event()
    stopped = []

    async def builder():
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    async def noop():
        pass

    class Media:
        async def stop(self):
            assert cancelled.is_set()
            stopped.append(True)

    task = asyncio.create_task(builder())
    client._media_pool_tasks.add(task)
    client.media_session_pools[2] = [Media()]
    client.storage = SimpleNamespace(save=noop)
    client.dispatcher = SimpleNamespace(stop=noop)
    await started.wait()
    await client.terminate()
    assert stopped == [True]
    assert client._media_pool_tasks == set()
    client.executor.shutdown(wait=True)
