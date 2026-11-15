import asyncio
import io
import os
from hashlib import sha256
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.crypto import aes
from pyrogram.errors import FileReferenceExpired, InternalServerError
from pyrogram.file_id import FileId, FileType
from pyrogram.methods.advanced import save_file as save_file_module
from tests.test_media import CHUNK_SIZE, FakeStorage, PART_SIZE, make_file_id

MB = 1024 * 1024


@pytest.mark.asyncio
async def test_upload_drain_survives_flood_pause(monkeypatch):
    """A flood wait on the last parts must not kill the upload (false stall)."""
    client = Client("flooddrain", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    monkeypatch.setattr(save_file_module, "STALL_TIMEOUT", 0.2)

    # Each part floods once (0.4s), then is acknowledged. With
    # STALL_TIMEOUT=0.2 the old drain logic would abort while the first
    # flood sleep was still running.
    from pyrogram.errors import FloodWait

    class PartFlooder:
        def __init__(self):
            self.calls = {}

        async def invoke(self, data, **kwargs):
            n = self.calls.get(data.file_part, 0)
            self.calls[data.file_part] = n + 1
            if n == 0:
                raise FloodWait(value=0.4)
            return True

    client.upload_sessions[2] = [PartFlooder()]

    result = await client.save_file(io.BytesIO(b"x" * (2 * PART_SIZE)))

    assert result.parts == 2
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_upload_still_raises_when_workers_hang(monkeypatch):
    """A genuine stall (hung workers, no flood activity) must still abort."""
    client = Client("hungdrain", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    monkeypatch.setattr(save_file_module, "STALL_TIMEOUT", 0.3)

    class Hung:
        async def invoke(self, data, **kwargs):
            await asyncio.Event().wait()  # never returns

    client.upload_sessions[2] = [Hung()]

    with pytest.raises(TimeoutError):
        await client.save_file(io.BytesIO(b"x" * (2 * PART_SIZE)))
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_upload_retries_transient_5xx():
    """A transient 5xx server error retries the same part instead of failing."""
    client = Client("five", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    calls = []

    class Flaky:
        async def invoke(self, data, **kwargs):
            calls.append(data.file_part)
            if len(calls) == 1:
                raise InternalServerError("INTERNAL_SERVER_ERROR")
            return True

    client.upload_sessions[2] = [Flaky()]

    result = await client.save_file(io.BytesIO(b"x" * (2 * PART_SIZE)))

    assert result.parts == 2
    assert sorted(calls) == [0, 0, 1]
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_file_reference_refresh_renews_and_retries(monkeypatch):
    """FILE_REFERENCE_EXPIRED is refreshed in place; the download succeeds."""
    client = Client("refrefresh", api_id=1, api_hash="test")
    client.storage = FakeStorage()

    data = os.urandom(3 * CHUNK_SIZE)
    old_ref = make_file_id().file_reference
    new_ref = b"refreshed_file_reference"

    class Expiring:
        def __init__(self, data):
            self.data = data
            self.refs = []

        async def invoke(self, query, **kwargs):
            self.refs.append(query.location.file_reference)
            if query.location.file_reference != new_ref:
                raise FileReferenceExpired("FILE_REFERENCE_EXPIRED")
            at = query.offset
            return raw.types.upload.File(
                bytes=self.data[at:at + query.limit], type=None, mtime=0
            )

    exp = Expiring(data)

    refresh_calls = []
    refreshed_file_id = FileId(
        file_type=FileType.DOCUMENT,
        dc_id=2,
        media_id=123456,
        access_hash=789012,
        file_reference=new_ref,
        thumbnail_size="",
    )

    async def fake_get_messages(chat_id, message_ids):
        refresh_calls.append((chat_id, tuple(message_ids)))
        return [SimpleNamespace(file_id=refreshed_file_id.encode())]

    async def fake_get_session(dc_id=None, **kwargs):
        return exp

    async def fake_pool(dc_id, n):
        return [exp]

    monkeypatch.setattr(client, "get_messages", fake_get_messages)
    monkeypatch.setattr(client, "get_session", fake_get_session)
    monkeypatch.setattr(client, "_get_media_session_pool", fake_pool)

    file_id = make_file_id()
    file_id._refresh_context = (100, 5)

    chunks = [chunk async for chunk in client.get_file(file_id, file_size=len(data))]

    assert b"".join(chunks) == data
    # The old reference was used, then every later request carried the new one.
    assert old_ref in exp.refs
    assert all(ref == new_ref for ref in exp.refs[exp.refs.index(old_ref) + 1:])
    assert 1 <= len(refresh_calls) <= 2
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_file_reference_refresh_gives_up_on_unchanged_reference(monkeypatch):
    """If the refreshed reference is identical, the error propagates instead of looping."""
    client = Client("refstuck", api_id=1, api_hash="test")
    client.storage = FakeStorage()

    old_ref = make_file_id().file_reference

    class AlwaysExpired:
        async def invoke(self, query, **kwargs):
            raise FileReferenceExpired("FILE_REFERENCE_EXPIRED")

    async def fake_get_messages(chat_id, message_ids):
        same = FileId(
            file_type=FileType.DOCUMENT,
            dc_id=2,
            media_id=123456,
            access_hash=789012,
            file_reference=old_ref,
            thumbnail_size="",
        )
        return [SimpleNamespace(file_id=same.encode())]

    async def fake_get_session(dc_id=None, **kwargs):
        return AlwaysExpired()

    monkeypatch.setattr(client, "get_messages", fake_get_messages)
    monkeypatch.setattr(client, "get_session", fake_get_session)

    file_id = make_file_id()
    file_id._refresh_context = (100, 5)

    with pytest.raises(FileReferenceExpired):
        async for _ in client.get_file(file_id, file_size=CHUNK_SIZE):
            pass
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_file_reference_refresh_requires_context():
    """Without a message context the refresh is a no-op returning False."""
    client = Client("nocontext", api_id=1, api_hash="test")

    assert await client._refresh_file_reference(make_file_id()) is False
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_cdn_download_pipelined(monkeypatch):
    """CDN redirect downloads decrypt, verify and reassemble correctly."""
    client = Client("cdn", api_id=1, api_hash="test")
    client.storage = FakeStorage()

    data = os.urandom(CHUNK_SIZE + 12345)
    key = os.urandom(32)
    iv = os.urandom(16)

    encrypted = []
    at = 0
    while at < len(data):
        part = data[at:at + CHUNK_SIZE]
        chunk_iv = iv[:-4] + (at // 16).to_bytes(4, "big")
        encrypted.append(aes.ctr256_encrypt(part, key, chunk_iv))
        at += CHUNK_SIZE

    # Hashes cover the decrypted chunk slices, matching the server contract
    # this implementation verifies against.
    hashes = [
        raw.types.FileHash(
            offset=i * CHUNK_SIZE,
            limit=len(part),
            hash=sha256(data[i * CHUNK_SIZE:i * CHUNK_SIZE + len(part)]).digest(),
        )
        for i, part in enumerate(encrypted)
    ]

    redirect = raw.types.upload.FileCdnRedirect(
        dc_id=2,
        file_token=b"cdn_token",
        encryption_key=key,
        encryption_iv=iv,
        file_hashes=hashes,
    )

    cdn_offsets = []

    class MainSession:
        async def invoke(self, query, **kwargs):
            assert isinstance(query, raw.functions.upload.GetFile)
            return redirect

        async def stop(self):
            pass

    class CdnSession:
        async def invoke(self, query, **kwargs):
            cdn_offsets.append(query.offset)
            return raw.types.upload.CdnFile(
                bytes=encrypted[query.offset // CHUNK_SIZE]
            )

        async def stop(self):
            pass

    async def fake_get_session(dc_id=None, **kwargs):
        return CdnSession() if kwargs.get("is_cdn") else MainSession()

    async def fake_pool(dc_id, n):
        return [MainSession()]

    monkeypatch.setattr(client, "get_session", fake_get_session)
    monkeypatch.setattr(client, "_get_media_session_pool", fake_pool)

    chunks = [
        chunk async for chunk in client.get_file(make_file_id(), file_size=len(data))
    ]

    assert b"".join(chunks) == data
    # Every chunk was fetched exactly once, in order, without re-fetching
    # past the end of the file.
    assert cdn_offsets == [0, CHUNK_SIZE]
    client.executor.shutdown(wait=True)
