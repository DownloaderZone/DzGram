from io import BytesIO

import pytest

from pyrogram import raw
from pyrogram.raw.all import layer
from pyrogram.raw.core import TLObject


@pytest.mark.parametrize("value", [
    raw.types.InputMediaWidget(
        width=320,
        height=240,
        html="<div></div>",
        allow_queries=True,
        public_data="{}",
    ),
    raw.types.MessageMediaWidget(
        width=320,
        height=240,
        payload=b"payload",
        public_data="{}",
        public_data_hash=123,
        widget_id=456,
    ),
    raw.types.UserWallet(
        address="EQCG_example_address",
        balance=100,
        public_key=b"key",
        state_init=b"init",
    ),
    raw.types.UpdateEditForumTopic(
        peer=raw.types.PeerChannel(channel_id=1),
        topic_id=2,
        title="New title",
        closed=True,
    ),
    raw.types.UpdateBotWidgetQuery(
        query_id=1,
        query_type=raw.types.WidgetQueryTypeData(),
        user_id=2,
        peer=raw.types.PeerUser(user_id=2),
        msg_id=3,
        chat_instance=4,
        chat_type="private",
        data=b"data",
        widget_id=5,
        wallet_card=None,
    ),
    raw.functions.channels.ToggleForum(
        channel=raw.types.InputChannel(channel_id=1, access_hash=0),
        enabled=True,
        tabs=False,
        sidebar=True,
    ),
    raw.functions.messages.GetBotWidgetQueryAnswer(
        peer=raw.types.InputPeerChannel(channel_id=1, access_hash=0),
        msg_id=42,
        query_type=raw.types.WidgetQueryTypeData(with_wallet=True),
        data=b"data",
    ),
])
def test_layer_233_wire_roundtrip(value):
    assert layer == 233
    encoded = value.write()
    buffer = BytesIO(encoded)
    decoded = TLObject.read(buffer)
    assert type(decoded) is type(value)
    assert decoded.write() == encoded
    assert buffer.tell() == len(encoded)
