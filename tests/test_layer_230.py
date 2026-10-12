from io import BytesIO

import pytest

from pyrogram import raw
from pyrogram.raw.all import layer
from pyrogram.raw.core import TLObject


@pytest.mark.parametrize("value", [
    raw.types.BotVerification(
        bot_id=123, icon=456,
        description=raw.types.TextWithEntities(
            text="Verified", entities=[raw.types.MessageEntityBold(offset=0, length=8)]
        )
    ),
    raw.types.Username(username="example", active=True, deletable=True, expired=True),
    raw.types.UpdateWalletState(state=raw.types.WalletState(
        address="address", public_key=b"key", balance=123, backup_enabled=True
    )),
    raw.functions.auth.InitFirebasePnvLogin(api_id=1, api_hash="test", except_ids=[123]),
    raw.functions.wallet.TonConnectSubmitResponse(session_id=1, msg_id=2, body=b"response"),
])
def test_layer_230_wire_roundtrip(value):
    assert layer == 230
    encoded = value.write()
    buffer = BytesIO(encoded)
    decoded = TLObject.read(buffer)
    assert type(decoded) is type(value)
    assert decoded.write() == encoded
    assert buffer.tell() == len(encoded)
