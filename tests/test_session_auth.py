import asyncio
from hashlib import sha1
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.errors import AuthKeyUnregistered, SecurityCheckMismatch
from pyrogram.methods.advanced.save_file import _create_upload_session, get_upload_sessions
from pyrogram.session import Auth, Session
from tests.test_media import FakeStorage


def test_auth_exchange_accepts_only_confirmed_key():
    key = b"k" * 256
    nonce = b"n" * 32
    digest = sha1(nonce + b"\x01" + sha1(key).digest()[:8]).digest()[4:20]
    answer = raw.types.DhGenOk(
        nonce=0, server_nonce=0,
        new_nonce_hash1=int.from_bytes(digest, "little", signed=True)
    )
    Auth._check_dh_answer(answer, nonce, key)
    with pytest.raises(SecurityCheckMismatch):
        Auth._check_dh_answer(answer, nonce, b"x" * 256)
    for rejected in (
        raw.types.DhGenRetry(nonce=0, server_nonce=0, new_nonce_hash2=0),
        raw.types.DhGenFail(nonce=0, server_nonce=0, new_nonce_hash3=0),
    ):
        with pytest.raises(SecurityCheckMismatch):
            Auth._check_dh_answer(rejected, nonce, key)


@pytest.mark.asyncio
async def test_unknown_transport_key_surfaces_without_restart():
    session = Session(SimpleNamespace(sleep_threshold=0), 2, b"k" * 256, False)
    session.is_connected.set()

    class Connection:
        async def recv(self):
            return (-404).to_bytes(4, "little", signed=True)

        async def send(self, packet):
            await session.recv_worker()

    session.connection = Connection()
    with pytest.raises(AuthKeyUnregistered):
        await session.send(raw.functions.Ping(ping_id=0))
    with pytest.raises(AuthKeyUnregistered):
        await session.invoke(raw.functions.Ping(ping_id=1))
    assert not session.is_connected.is_set()
    assert not session.results


@pytest.mark.asyncio
async def test_foreign_upload_reuses_authorized_dc_key(monkeypatch):
    client = Client("foreign_upload", api_id=1, api_hash="test")
    client.storage = FakeStorage()
    calls = []

    async def get_session(dc_id):
        calls.append(dc_id)
        return SimpleNamespace(auth_key=b"authorized")

    async def get_option(*args, **kwargs):
        return SimpleNamespace(ip_address="127.0.0.1", port=443)

    class Upload:
        MAX_RETRIES = 10

        def __init__(self, *args, **kwargs):
            self.auth_key = args[2]

        async def start(self, **kwargs):
            assert kwargs["max_attempts"] == self.MAX_RETRIES

    client.get_session = get_session
    client.get_dc_option = get_option
    monkeypatch.setattr("pyrogram.methods.advanced.save_file.Session", Upload)
    try:
        session = await _create_upload_session(client, 4)
        assert calls == [4]
        assert session.auth_key == b"authorized"
    finally:
        client.executor.shutdown(wait=True)


@pytest.mark.asyncio
async def test_upload_pool_keeps_ready_sessions_when_growth_cancelled(monkeypatch):
    client = Client("upload_cancel", api_id=1, api_hash="test")
    ready = asyncio.Event()
    slow = asyncio.Event()
    calls = []
    session = SimpleNamespace()

    async def create(*args):
        calls.append(True)
        if len(calls) == 1:
            ready.set()
            return session
        slow.set()
        await asyncio.Event().wait()

    monkeypatch.setattr("pyrogram.methods.advanced.save_file._create_upload_session", create)
    task = asyncio.create_task(get_upload_sessions(client, 2, 3))
    try:
        await ready.wait()
        await slow.wait()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        assert client.upload_sessions[2] == [session]
    finally:
        client.executor.shutdown(wait=True)
