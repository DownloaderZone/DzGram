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
    def __init__(self, data: bytes, delay: float = 0.0, stats: dict = None):
        self.data = data
        self.delay = delay
        self.stats = stats if stats is not None else {
            "requests": [], "max_inflight": 0, "inflight": 0
        }
        self.is_connected = asyncio.Event()
        self.is_connected.set()

    async def invoke(self, query, sleep_threshold=None, **kwargs):
        assert isinstance(query, raw.functions.upload.GetFile)

        stats = self.stats
        stats["requests"].append(query.offset)
        stats["inflight"] += 1
        stats["max_inflight"] = max(stats["max_inflight"], stats["inflight"])

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
            stats["inflight"] -= 1


class FakeStorage:
    async def dc_id(self):
        return 2

    async def auth_key(self):
        return b"fake_auth_key"

    async def test_mode(self):
        return False


class FakeUploadSession:
    def __init__(self, delay: float = 0.0, stats: dict = None):
        self.delay = delay
        self.is_connected = asyncio.Event()
        self.is_connected.set()
        self.invoked = []
        self.stats = stats if stats is not None else {
            "max_inflight": 0, "inflight": 0
        }
        self.fail_on = None
        self.fail_exc = ConnectionError("simulated part failure")

    async def start(self):
        pass

    async def stop(self):
        pass

    async def invoke(self, data, **kwargs):
        if isinstance(data, raw.functions.upload.SaveFilePart):
            assert getattr(data, "file_total_parts", None) is None
        else:
            assert data.file_total_parts >= data.file_part + 1

        stats = self.stats
        stats["inflight"] += 1
        stats["max_inflight"] = max(stats["max_inflight"], stats["inflight"])

        try:
            if self.fail_on is not None and data.file_part == self.fail_on:
                raise self.fail_exc

            self.invoked.append(data.file_part)

            # Force overlapping in-flight parts.
            await asyncio.sleep(self.delay or random.random() * 0.002)
            return True
        finally:
            stats["inflight"] -= 1


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


def seed_media(client, data: bytes, sessions: int = 3, delay: float = 0.0):
    """Seed the client's media session pool with fake sessions sharing stats."""
    stats = {"requests": [], "max_inflight": 0, "inflight": 0}
    pool = [FakeMediaSession(data, delay=delay, stats=stats) for _ in range(sessions)]
    client.storage = FakeStorage()
    client.media_sessions[2] = pool[0]
    client.media_session_pools[2] = pool
    return pool, stats


def seed_upload(client, sessions):
    client.storage = FakeStorage()
    client.media_session_pools[2] = list(sessions)


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
        _, stats = seed_media(client, data, delay=0.001)

        result = await collect(client, make_file_id(), file_size=len(data))

        assert result == data
        assert sorted(stats["requests"]) == [0, CHUNK_SIZE, 2 * CHUNK_SIZE]
        assert stats["max_inflight"] > 1

    async def test_parallel_download_unknown_size(self, make_client):
        client = make_client()
        data = os.urandom(3 * CHUNK_SIZE + 128 * 1024)
        _, stats = seed_media(client, data, delay=0.001)

        result = await collect(client, make_file_id())

        assert result == data
        # Without a known size the download falls back to sequential chunks.
        assert stats["max_inflight"] == 1
        assert sorted(stats["requests"]) == [0, CHUNK_SIZE, 2 * CHUNK_SIZE, 3 * CHUNK_SIZE]

    async def test_download_single_chunk_file(self, make_client):
        client = make_client()
        data = os.urandom(64 * 1024)
        _, stats = seed_media(client, data)

        result = await collect(client, make_file_id(), file_size=len(data))

        assert result == data
        assert stats["requests"] == [0]

    async def test_download_limit_and_offset(self, make_client):
        client = make_client()
        data = os.urandom(4 * CHUNK_SIZE)
        _, stats = seed_media(client, data)

        result = await collect(client, make_file_id(), file_size=len(data), limit=2)

        assert result == data[: 2 * CHUNK_SIZE]
        assert sorted(stats["requests"]) == [0, CHUNK_SIZE]

        stats["requests"].clear()
        stats["max_inflight"] = 0

        result = await collect(client, make_file_id(), file_size=len(data), limit=2, offset=1)

        assert result == data[CHUNK_SIZE: 3 * CHUNK_SIZE]
        assert sorted(stats["requests"]) == [CHUNK_SIZE, 2 * CHUNK_SIZE]

    async def test_download_workers_capped_by_size(self, make_client):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE)
        _, stats = seed_media(client, data)

        await collect(client, make_file_id(), file_size=len(data))

        assert stats["max_inflight"] <= 2

    async def test_download_progress(self, make_client):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE + 256 * 1024)
        seed_media(client, data)

        calls = []

        async def progress(current, total, tag):
            calls.append((current, total, tag))

        await collect(
            client, make_file_id(), file_size=len(data),
            progress=progress, progress_args=("tag",)
        )

        assert calls and calls[-1] == (len(data), len(data), "tag")

    async def test_download_stop_transmission(self, make_client):
        client = make_client()
        data = os.urandom(12 * CHUNK_SIZE)
        # A single worker keeps the download slow enough (12 * ~0.15s) for the
        # 0.5s progress reporter to tick before the file completes.
        seed_media(client, data, sessions=1, delay=0.15)
        client.download_workers = 1

        with pytest.raises(pyrogram.StopTransmission):
            async for _ in client.get_file(
                make_file_id(),
                file_size=len(data),
                progress=lambda current, total: (_ for _ in ()).throw(pyrogram.StopTransmission)
            ):
                pass

    async def test_handle_download_write_mode(self, make_client, tmp_path):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE + 256 * 1024)
        seed_media(client, data, delay=0.001)

        result = await client.handle_download(
            (make_file_id(), str(tmp_path), "file.bin", False, len(data), None, ())
        )

        assert result == str(tmp_path / "file.bin")
        assert (tmp_path / "file.bin").read_bytes() == data

    async def test_handle_download_in_memory(self, make_client, tmp_path):
        client = make_client()
        data = os.urandom(2 * CHUNK_SIZE + 256 * 1024)
        seed_media(client, data, delay=0.001)

        result = await client.handle_download(
            (make_file_id(), str(tmp_path), "file.bin", True, len(data), None, ())
        )

        assert isinstance(result, io.BytesIO)
        assert result.name == "file.bin"
        assert result.getvalue() == data


@pytest.mark.asyncio
class TestParallelUpload:
    async def test_small_file_upload(self, make_client):
        client = make_client()
        data = os.urandom(1 * MB + 123)
        sessions = [FakeUploadSession()]
        seed_upload(client, sessions)

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        result = await client.save_file(fp)

        assert isinstance(result, raw.types.InputFile)
        assert result.name == "test.bin"
        assert result.parts == math.ceil(len(data) / PART_SIZE)
        assert sorted(sessions[0].invoked) == list(range(result.parts))

    async def test_big_file_upload_parallel(self, make_client):
        client = make_client()
        data = os.urandom(12 * MB + 123)
        # Each part takes longer than the token-bucket dispatch interval
        # (1 / 50 s), so multiple parts must be in flight at once.
        stats = {"max_inflight": 0, "inflight": 0}
        sessions = [FakeUploadSession(delay=0.03, stats=stats) for _ in range(4)]
        seed_upload(client, sessions)

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        result = await client.save_file(fp)

        assert isinstance(result, raw.types.InputFileBig)
        assert result.parts == math.ceil(len(data) / PART_SIZE)

        all_parts = sorted(p for s in sessions for p in s.invoked)
        assert all_parts == list(range(len(all_parts)))
        assert stats["max_inflight"] > 1

    async def test_upload_progress(self, make_client):
        client = make_client()
        data = os.urandom(12 * MB)
        seed_upload(client, [FakeUploadSession() for _ in range(4)])

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        calls = []
        await client.save_file(
            fp, progress=lambda current, total: calls.append((current, total))
        )

        assert calls and calls[-1] == (len(data), len(data))

    async def test_upload_worker_failure(self, make_client):
        client = make_client()
        data = os.urandom(12 * MB)
        failing = FakeUploadSession()
        failing.fail_on = 0
        failing.fail_exc = RuntimeError("simulated part failure")
        seed_upload(client, [failing] + [FakeUploadSession() for _ in range(3)])

        fp = io.BytesIO(data)
        fp.name = "test.bin"

        with pytest.raises(RuntimeError):
            await client.save_file(fp)