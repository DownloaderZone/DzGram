import asyncio
from types import SimpleNamespace

import pytest

from pyrogram import Client, raw
from pyrogram.errors import AuthKeyUnregistered


@pytest.mark.asyncio
async def test_string_channel_id_resolves_as_chat_not_phone():
    client = Client("peer", api_id=1, api_hash="test")
    client.is_connected = True
    expected = raw.types.InputPeerChannel(channel_id=3988019621, access_hash=123)
    ids = []

    async def by_id(peer_id):
        ids.append(peer_id)
        assert peer_id == -1003988019621
        return expected

    client.storage = SimpleNamespace(get_peer_by_id=by_id)
    assert await client.resolve_peer(" -1003988019621 ") is expected
    assert ids == [-1003988019621]
    client.executor.shutdown(wait=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["state", "me"])
async def test_revoked_user_session_is_closed_without_overwriting_key(stage):
    client = Client("revoked", api_id=1, api_hash="test")
    disconnected = []

    async def connect():
        client.is_connected = True
        return True

    async def invoke(*args):
        if stage == "state":
            raise AuthKeyUnregistered()

    async def get_me():
        raise AuthKeyUnregistered()

    async def disconnect():
        disconnected.append(True)
        client.is_connected = False

    client.connect = connect
    client.invoke = invoke
    client.get_me = get_me
    client.disconnect = disconnect
    with pytest.raises(AuthKeyUnregistered):
        await client.start()
    assert disconnected == [True]
    assert not client.is_connected
    client.executor.shutdown(wait=True)
