import asyncio
import io
from io import BytesIO
import threading
import time
from hashlib import md5, sha256
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.errors import FloodWait
from pyrogram.methods.rate_limiter import AdaptiveBucket
from pyrogram.session import Session
from tests.test_media import FakeStorage, PART_SIZE, CHUNK_SIZE, make_file_id


@pytest.mark.asyncio
async def test_cdn_download_reuses_redirect_hashes_and_writes_file(monkeypatch):
    client = Client("cdn", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    data = b"cdn data"
    hashes = [raw.types.FileHash(offset=0, limit=len(data), hash=sha256(data).digest())]
    stopped = []

    class API(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            assert isinstance(query, raw.functions.upload.GetFile)
            return raw.types.upload.FileCdnRedirect(
                dc_id=2, file_token=b"token", encryption_key=b"k" * 32,
                encryption_iv=b"i" * 16, file_hashes=hashes
            )

    class CDN:
        async def invoke(self, query, **kwargs):
            assert isinstance(query, raw.functions.upload.GetCdnFile)
            return raw.types.upload.CdnFile(bytes=data)

        async def stop(self):
            stopped.append(True)

    async def get_session(*args, **kwargs):
        return CDN() if kwargs.get("is_cdn") else API()

    client.get_session = get_session
    monkeypatch.setattr("pyrogram.client.aes.ctr256_decrypt", lambda data, *args: data)
    output = io.BytesIO()
    result = b"".join([chunk async for chunk in client.get_file(
        make_file_id(), file_size=len(data), _write_file=output
    )])
    assert result == data
    assert output.getvalue() == data
    assert stopped == [True]
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_upload_uses_new_ready_session_before_expansion_finishes():
    client = Client("incremental", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    client.storage = FakeStorage()
    used = asyncio.Event()

    class Media:
        def __init__(self, new=False):
            self.new = new
            self.dc_id = 2
            self.is_connected = asyncio.Event()
            self.is_connected.set()

        async def invoke(self, query, **kwargs):
            if self.new:
                used.set()
            await asyncio.wait_for(used.wait(), 1)
            return True

    client.session = Media()

    async def expand(*args):
        client.media_session_pools[2] = [Media(new=True)]
        await asyncio.Event().wait()

    client._get_media_session_pool = expand
    result = await asyncio.wait_for(client.save_file(io.BytesIO(b"x" * (8 * PART_SIZE))), 2)
    assert result.parts == 8
    assert used.is_set()
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_download_uses_ready_media_before_full_pool_finishes():
    client = Client("incremental_download", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    used = asyncio.Event()
    builders = []

    class Media(Session):
        def __init__(self, new=False):
            self.new = new
            self.is_connected = asyncio.Event()
            self.is_connected.set()

        async def invoke(self, query, **kwargs):
            if query.offset:
                if self.new:
                    used.set()
                await asyncio.wait_for(used.wait(), 1)
            return raw.types.upload.File(bytes=b"x" * CHUNK_SIZE, type=None, mtime=0)

    async def get_session(*args, **kwargs):
        return Media()

    async def expand(*args):
        builders.append(asyncio.current_task())
        client.media_session_pools[2] = [Media(new=True)]
        await asyncio.Event().wait()

    client.get_session = get_session
    client._get_media_session_pool = expand
    async def collect():
        return b"".join([chunk async for chunk in client.get_file(make_file_id(), file_size=20 * CHUNK_SIZE)])
    result = await asyncio.wait_for(collect(), 2)
    assert len(result) == 20 * CHUNK_SIZE
    assert used.is_set()
    for task in builders:
        task.cancel()
    await asyncio.gather(*builders, return_exceptions=True)
    client.executor.shutdown(wait=True)


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
async def test_bot_upload_starts_on_main_session_without_media_setup():
    client = Client("api_upload", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    client.storage = FakeStorage()
    sent = []

    class API:
        dc_id = 2
        is_connected = asyncio.Event()

        async def invoke(self, query, **kwargs):
            sent.append(query.file_part)
            return True

    client.session = API()
    client.session.is_connected.set()

    async def slow_pool(*args):
        await asyncio.Event().wait()

    client._get_media_session_pool = slow_pool
    result = await asyncio.wait_for(client.save_file(io.BytesIO(b"x" * (4 * PART_SIZE))), 1)
    assert result.parts == 4
    assert sorted(sent) == [0, 1, 2, 3]
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_bot_download_continues_while_media_pool_is_blocked():
    client = Client("api_download", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    data = b"x" * (4 * CHUNK_SIZE)
    background = []

    class API(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            await asyncio.sleep(0)
            return raw.types.upload.File(bytes=data[query.offset:query.offset + query.limit], type=None, mtime=0)

    async def session(*args, **kwargs):
        return API()

    async def slow_pool(*args):
        background.append(asyncio.current_task())
        await asyncio.Event().wait()

    client.get_session = session
    client._get_media_session_pool = slow_pool
    budget = client.read_ahead_slots._value

    async def collect():
        return b"".join([chunk async for chunk in client.get_file(make_file_id(), file_size=len(data))])

    assert await asyncio.wait_for(collect(), 1) == data
    assert client.read_ahead_slots._value == budget
    for task in background:
        task.cancel()
    await asyncio.gather(*background, return_exceptions=True)
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


@pytest.mark.asyncio
async def test_download_ramp_reaches_ceiling_quickly_for_all_users():
    # Regression: non-bot/non-premium downloads ramped at 0.5 parts/s per
    # tick, needing >5 minutes to reach the 200 ceiling. Every account now
    # ramps at the same aggressive step.
    client = Client("ramp", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=False, is_premium=False)
    bucket = AdaptiveBucket(rate=30, ceiling=200, burst=45, step=8.0,
                            recover_interval=0.05)
    for _ in range(40):
        time.sleep(0.05)
        bucket.on_success()
    assert bucket.rate >= 195.0, f"ramp too slow: {bucket.rate} after 2s"

    # The pre-fix step of 0.5 parts/s per tick barely moves off the floor.
    slow = AdaptiveBucket(rate=30, ceiling=200, burst=45, step=0.5)
    for _ in range(40):
        time.sleep(0.05)
        slow.on_success()
    assert slow.rate < 100.0
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_download_write_is_offloaded_to_executor(monkeypatch):
    # Regression: write_at ran synchronously on the event loop, blocking all
    # workers and network I/O for the duration of each disk write. It must
    # now run in the client's thread-pool executor.
    import os
    import shutil
    import tempfile

    client = Client("offload", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)
    assert client.executor is not None

    calls = []
    import pyrogram.client as client_module
    real_write_at = client_module.write_at

    def tracked_write_at(fd, data, offset):
        calls.append(threading.current_thread() is not threading.main_thread())
        return real_write_at(fd, data, offset)

    monkeypatch.setattr(client_module, "write_at", tracked_write_at)

    out_dir = tempfile.mkdtemp()
    out_path = os.path.join(out_dir, "out.bin")
    file = open(out_path, "w+b")

    class API(Session):
        def __init__(self):
            pass

        async def invoke(self, query, **kwargs):
            return raw.types.upload.File(
                bytes=b"x" * CHUNK_SIZE, type=None, mtime=0
            )

    async def get_session(dc_id, is_media=False, **kwargs):
        return API()

    async def pool(*args):
        return [API()]

    client.get_session = get_session
    client._get_media_session_pool = pool
    try:
        size = 3 * CHUNK_SIZE
        async for chunk in client.get_file(
            make_file_id(), file_size=size, _write_file=file
        ):
            pass
        assert os.path.getsize(out_path) == size
        assert calls and all(calls), "write_at must not run on the event-loop thread"
    finally:
        file.close()
        client.executor.shutdown(wait=True)
        shutil.rmtree(out_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_send_video_rejected_cover_falls_back_to_no_cover():
    """A cover Telegram rejects (PHOTO_SAVE_FILE_INVALID) must not fail the send."""
    from pyrogram.errors import BadRequest

    from PIL import Image

    cover_buf = BytesIO()
    cover_buf.name = "cover.jpg"
    Image.new("RGB", (640, 360), "red").save(cover_buf, format="JPEG")
    cover_buf.seek(0)
    jpeg = cover_buf

    client = Client("cover", api_id=1, api_hash="test")
    client.me = SimpleNamespace(is_bot=True, is_premium=False)

    sent = []
    seen_uploads = []

    async def invoke(query, **kwargs):
        if isinstance(query, raw.functions.messages.UploadMedia):
            seen_uploads.append(query)
            raise BadRequest("PHOTO_SAVE_FILE_INVALID")
        assert isinstance(query, raw.functions.messages.SendMedia)
        sent.append(query)
        msg = raw.types.Message(
            id=1, peer_id=raw.types.PeerUser(user_id=1),
            message="", date=0,
            media=raw.types.MessageMediaDocument(
                document=raw.types.Document(
                    id=1, access_hash=1, file_reference=b"", mime_type="video/mp4",
                    size=1, date=0, dc_id=1, attributes=[]
                )
            )
        )
        return raw.types.Updates(
            updates=[raw.types.UpdateNewMessage(message=msg, pts=1, pts_count=1)],
            users=[], chats=[], seq=0, date=0
        )

    client.invoke = invoke

    async def resolve_peer(peer, *args, **kwargs):
        return raw.types.InputPeerEmpty()

    client.resolve_peer = resolve_peer
    async def fake_save_file(*a, **k):
        return raw.types.InputFile(id=1, parts=1, name="f", md5_checksum="x")

    client.save_file = fake_save_file
    client.guess_mime_type = lambda *a: "video/mp4"

    from pyrogram import utils as _utils

    async def fake_parse(self, text, parse_mode, entities):
        return {"message": "", "entities": []}

    monkey = pytest.MonkeyPatch()
    monkey.setattr(_utils, "parse_text_entities", fake_parse)
    monkey.setattr(_utils, "_get_reply_message_parameters", _asyncfn(None))

    from pyrogram.types.messages_and_media import message as message_mod

    async def fake_message_parse(client, raw_msg, users, chats, **kwargs):
        return "MESSAGE"

    monkey.setattr(message_mod.Message, "_parse", staticmethod(fake_message_parse))
    try:
        video = io.BytesIO(b"video")
        video.name = "video.mp4"
        await client.send_video(123, video, cover=jpeg, caption="")
    finally:
        monkey.undo()
        client.executor.shutdown(wait=True)

    # Cover upload was attempted once and rejected, then the send still went out.
    assert len(seen_uploads) == 1
    assert len(sent) == 1
    media = sent[0].media
    assert isinstance(media, raw.types.InputMediaUploadedDocument)
    assert media.video_cover is None


def _asyncfn(value):
    async def inner(*args, **kwargs):
        return value
    return inner


def test_prepare_photo_upload_reencodes_covers_to_clean_jpeg():
    """Anything sent as a photo/cover comes out as a baseline RGB JPEG <=2560px."""
    from PIL import Image

    from pyrogram import utils

    # CMYK JPEG (a Telegram reject trigger) re-encodes to RGB.
    cmyk = BytesIO()
    cmyk.name = "cmyk.jpg"
    Image.new("CMYK", (100, 80), (0, 255, 255, 0)).save(cmyk, format="JPEG")

    out = utils.prepare_photo_upload(cmyk)
    with Image.open(out) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert not image.info.get("progression", False)

    # Oversized PNG gets downscaled to the 2560px cap and converted.
    big = BytesIO()
    big.name = "big.png"
    Image.new("RGB", (3000, 100), "red").save(big, format="PNG")

    out = utils.prepare_photo_upload(big)
    with Image.open(out) as image:
        assert image.format == "JPEG"
        assert max(image.size) <= utils._PHOTO_MAX_SIDE

    # A mislabeled WebP masquerading as .jpg is re-encoded, not passed through.
    webp = BytesIO()
    webp.name = "cover.jpg"
    Image.new("RGB", (40, 40), "blue").save(webp, format="WEBP")

    out = utils.prepare_photo_upload(webp)
    with Image.open(out) as image:
        assert image.format == "JPEG"


def test_prepare_photo_upload_rejects_truncated_jpeg_without_pillow(monkeypatch):
    """Without Pillow, a truncated JPEG fails locally, not at Telegram."""
    from pyrogram import utils

    truncated = BytesIO(bytes.fromhex("ffd8ffe000104a4649460001") + b"garbage")
    truncated.name = "cover.jpg"

    monkeypatch.setattr(utils, "HAS_PILLOW", False)
    with pytest.raises(ValueError, match="truncated"):
        utils.prepare_photo_upload(truncated)


def test_prepare_photo_upload_passes_structurally_valid_jpeg(monkeypatch):
    """Without Pillow, a real JPEG with matching extension is kept as-is."""
    from pyrogram import utils

    from PIL import Image

    jpeg = BytesIO()
    jpeg.name = "cover.jpg"
    Image.new("RGB", (64, 64), "red").save(jpeg, format="JPEG")

    monkeypatch.setattr(utils, "HAS_PILLOW", False)
    assert utils.prepare_photo_upload(jpeg) is jpeg


def test_warpcrypto_api_contract():
    """Pin the warpcrypto surface this library depends on (2.1.0 semantics)."""
    import warpcrypto
    from pyrogram.crypto import aes

    # IGE roundtrip with a 32-byte IV (Telegram MTProto layout).
    key = bytes(range(32))
    iv = bytes(range(32))
    data = bytes(range(64))
    assert aes.ige256_decrypt(aes.ige256_encrypt(data, key, iv), key, iv) == data

    # CTR roundtrip; the iv buffer must advance so the stream stays continuous
    # across successive calls on the same key (state byte stays 0 on 2.1.0).
    iv_b = bytearray(range(16))
    state = bytearray(1)
    enc = aes.ctr256_encrypt(data, key, iv_b, state)
    assert aes.ctr256_decrypt(enc, key, bytearray(range(16)), bytearray(1)) == data
    assert bytes(iv_b[-1:]) != b"\x0e"  # last counter byte advanced by 4 blocks

    # In-place variants mutate the buffer and return None on 2.1.0.
    buf = bytearray(data)
    aes.ctr256_encrypt_inplace(buf, key, bytearray(range(16)), bytearray(1))
    assert buf != bytearray(data)

    # Batch layout: sizes = flat int32 LE (4*n), ivs = 16*n, states = n.
    import struct

    flat = bytes(range(96))
    sizes = bytearray(struct.pack("<2i", 48, 48))
    enc_batch = aes.ctr256_encrypt_batch(flat, sizes, key, bytearray(32), bytearray(2))
    assert aes.ctr256_decrypt_batch(enc_batch, sizes, key, bytearray(32), bytearray(2)) == flat
