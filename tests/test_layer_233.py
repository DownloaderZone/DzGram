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
    raw.types.AgentProvider(
        id="provider",
        title="Provider",
        vendor="Vendor",
        key_url="https://example.com",
        icon_emoji_id=789,
        models_searchable=True,
    ),
    raw.types.FeedPosition(
        date=123,
        peer=raw.types.PeerUser(user_id=1),
        id=2,
    ),
    raw.types.UpdateBotWidgetQuery(
        query_id=1,
        user_id=2,
        peer=raw.types.PeerUser(user_id=2),
        msg_id=3,
        chat_instance=4,
        chat_type="private",
        data=b"data",
        widget_id=5,
    ),
    raw.functions.feed.GetFeed(
        filter_id=0,
        add_offset=0,
        limit=20,
        hash=0,
        offset_position=raw.types.FeedPosition(
            date=1, peer=raw.types.PeerUser(user_id=1), id=2
        ),
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
