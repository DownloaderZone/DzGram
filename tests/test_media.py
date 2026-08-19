import asyncio
import io
import math
import os
import random

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.file_id import FileId, FileType

MB = 1024 * 1024
CHUNK_SIZE = MB
PART_SIZE = 512 * 1024


def make_file_id(dc_id: int = 2, file_type: FileType = FileType.DOCUMENT):
    return FileId(
        dc_id=dc_id,
        media_id=123456,
        access_hash=789012,
        file_reference=b"test_file_reference",
        file_type=file_type,
        thumbnail_size="",
    )


class FakeMediaSession:
    def __init__(self, data: bytes, delay: float = 0.0):
        self.data = data
        self.delay = delay
        self.requests = []
        self.max_inflight = 0
        self._inflight = 0

    async def invoke(self, query, sleep_threshold=None, **kwargs):
        assert isinstance(query, raw.functions.upload.GetFile)

        self.requests.append(query.offset)
        self._inflight += 1
        self.max_inflight = max(self.max_inflight, self._inflight)

        try:
            if self.delay:
                await asyncio.sleep(self.delay * random.random())

            # Telegram returns an empty chunk for offsets beyond the end of the file.
            return raw.types.upload.File(
                bytes=self.data[query.offset: query.offset + query.limit],
                type=None,
                mtime=0
            )
        finally:
            self._inflight -= 1


class FakeStorage:
    async def dc_id(self):
        return 2

    async def auth_key(self):
        return b"fake_auth_key"

    async def test_mode(self):
        return False


class FakeUploadSession:
    def __init__(self):
        self.invoked = []
        self.max_inflight = 0
        self._inflight = 0
        self.fail_on = None

    async def start(self):
        pass

    async def stop(self):
        pass

    async def invoke(self, data, **kwargs):
        if isinstance(data, raw.functions.upload.SaveFilePart):
            assert getattr(data, "file_total_parts", None) is None
        else:
            assert data.file_total_parts >= data.file_part + 1

        self._inflight += 1
        self.max_inflight = max(self.max_inflight, self._inflight)

        try:
            if self.fail_on is not None and data.file_part == self.fail_on:
                raise ConnectionError("simulated part failure")

            self.invoked.append(data.file_part)

            # Force overlapping in-flight parts.
            await asyncio.sleep(random.random() * 0.002)
            return True
        finally:
            self._inflight -= 1


@pytest.fixture
def make_client():
    # The Client must be created inside a running event loop so that
    # ``Client.loop`` points to the loop the test coroutine runs on.
    def _make(**kwargs):
        return pyrogram.Client(
            "test_media",
            api_id=1,
            api_hash="test",
            download_workers=8,
            upload_workers=4,
            **kwargs
        )

    return _make


async def collect(app, file_id, **kwargs):
    chunks = []
    async for chunk in app.get_file(file_id, **kwargs):
        chunks.append(chunk)
    return b"".join(chunks)


@pytest.mark.asyncio
class TestParallelDownload:
    async def test_parallel_download_known_size(self, make_client):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE + 512 * 1024)
        session = FakeMediaSession(data, delay=0.001)
        client.media_sessions[2] = session

        result = await collect(client, make_file_id(), file_size=len(data))

        assert result == data
        assert session.requests[0] == 0
        assert all(b - a == CHUNK_SIZE for a, b in zip(session.requests, session.requests[1:]))
        assert session.max_inflight > 1

    async def test_parallel_download_unknown_size(self, make_client):
        client = make_client()
        data = os.urandom(3 * CHUNK_SIZE + 128 * 1024)
        session = FakeMediaSession(data, delay=0.001)
        client.media_sessions[2] = session

        result = await collect(client, make_file_id())

        assert result == data
        assert session.max_inflight > 1

    async def test_download_single_chunk_file(self, make_client):
        client = make_client()
        data = os.urandom(64 * 1024)
        session = FakeMediaSession(data)
        client.media_sessions[2] = session

        result = await collect(client, make_file_id(), file_size=len(data))

        assert result == data
        assert session.requests == [0]

    async def test_download_limit_and_offset(self, make_client):
        client = make_client()
        data = os.urandom(4 * CHUNK_SIZE)
        session = FakeMediaSession(data)
        client.media_sessions[2] = session

        result = await collect(client, make_file_id(), file_size=len(data), limit=2)

        assert result == data[: 2 * CHUNK_SIZE]
        assert len(session.requests) == 2

        session.requests.clear()
        session.max_inflight = 0
        result = await collect(client, make_file_id(), file_size=len(data), limit=2, offset=1)

        assert result == data[CHUNK_SIZE: 3 * CHUNK_SIZE]
        assert session.requests == [CHUNK_SIZE, 2 * CHUNK_SIZE]

    async def test_download_workers_capped_by_size(self, make_client):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE)
        session = FakeMediaSession(data)
        client.media_sessions[2] = session

        await collect(client, make_file_id(), file_size=len(data))

        assert session.max_inflight <= 2

    async def test_download_progress(self, make_client):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE + 256 * 1024)
        session = FakeMediaSession(data)
        client.media_sessions[2] = session

        calls = []

        async def progress(current, total, tag):
            calls.append((current, total, tag))

        await collect(
            client, make_file_id(), file_size=len(data),
            progress=progress, progress_args=("tag",)
        )

        assert len(calls) == 3
        assert calls[-1] == (len(data), len(data), "tag")

    async def test_download_stop_transmission(self, make_client):
        client = make_client()
        data = os.urandom(3 * CHUNK_SIZE)
        session = FakeMediaSession(data, delay=0.005)
        client.media_sessions[2] = session

        with pytest.raises(pyrogram.StopTransmission):
            async for _ in client.get_file(
                make_file_id(),
                file_size=len(data),
                progress=lambda current, total: (_ for _ in ()).throw(pyrogram.StopTransmission)
            ):
                pass


@pytest.mark.asyncio
class TestParallelUpload:
    def _patch_sessions(self, client, monkeypatch, sessions):
        client.storage = FakeStorage()
        pool = list(sessions)

        def factory(*args, **kwargs):
            return pool.pop(0) if pool else FakeUploadSession()

        monkeypatch.setattr("pyrogram.methods.advanced.save_file.Session", factory)

    async def test_small_file_upload(self, make_client, monkeypatch):
        client = make_client()
        data = os.urandom(1 * MB + 123)
        self._patch_sessions(client, monkeypatch, [FakeUploadSession()])

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        result = await client.save_file(fp)

        assert isinstance(result, raw.types.InputFile)
        assert result.name == "test.bin"
        assert result.parts == math.ceil(len(data) / PART_SIZE)

    async def test_big_file_upload_parallel(self, make_client, monkeypatch):
        client = make_client()
        data = os.urandom(12 * MB + 123)
        sessions = [FakeUploadSession() for _ in range(3)]
        self._patch_sessions(client, monkeypatch, sessions)

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        result = await client.save_file(fp)

        assert isinstance(result, raw.types.InputFileBig)
        assert result.parts == math.ceil(len(data) / PART_SIZE)

        all_parts = sorted(p for s in sessions for p in s.invoked)
        assert all_parts == list(range(len(all_parts)))
        assert max(s.max_inflight for s in sessions) > 1

    async def test_upload_progress(self, make_client, monkeypatch):
        client = make_client()
        data = os.urandom(12 * MB)
        self._patch_sessions(client, monkeypatch, [FakeUploadSession() for _ in range(3)])

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        calls = []
        await client.save_file(
            fp, progress=lambda current, total: calls.append((current, total))
        )

        assert len(calls) == math.ceil(len(data) / PART_SIZE)
        assert calls[-1] == (len(data), len(data))

    async def test_upload_worker_failure(self, make_client, monkeypatch):
        client = make_client()
        data = os.urandom(12 * MB)
        failing = FakeUploadSession()
        failing.fail_on = 0
        self._patch_sessions(client, monkeypatch, [failing])

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        result = await client.save_file(fp)

        # The failed part is no longer silently swallowed: the upload aborts
        # and returns None instead of a corrupt InputFile.
        assert result is None
