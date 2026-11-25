from io import BytesIO

import pytest

from pyrogram import raw, types
from pyrogram.raw.all import layer
from pyrogram.raw.core import TLObject


def forum_topic():
    return raw.types.ForumTopic(
        id=1,
        date=0,
        peer=raw.types.PeerChannel(channel_id=1),
        title="Topic",
        icon_color=0,
        top_message=1,
        read_inbox_max_id=0,
        read_outbox_max_id=0,
        unread_count=0,
        unread_mentions_count=0,
        unread_reactions_count=0,
        unread_poll_votes_count=0,
        from_id=raw.types.PeerUser(user_id=1),
        notify_settings=raw.types.PeerNotifySettings(),
    )


@pytest.mark.parametrize("value", [
    raw.types.InputAiComposeStyle(
        emojify=True,
        proofread=True,
        tone=raw.types.InputAiComposeToneDefault(tone="friendly"),
        to_lang="en",
    ),
    raw.types.TranscriptionModel(
        document=raw.types.DocumentEmpty(id=1),
        languages=["en", "ru"],
        version=2,
    ),
    raw.types.MessageActionBotInvite(inviter_id=42),
    raw.types.MessageActionStarGiftOnchainOffer(
        offer_id=7,
        gift=raw.types.StarGiftUnique(
            id=1,
            gift_id=2,
            title="Gift",
            slug="gift-1",
            num=1,
            attributes=[],
            availability_issued=1,
            availability_total=10,
            onchain_sale=True,
            offer_min_amount=100,
            fee_bps=250,
        ),
        amount=100,
        fee_bps=250,
        expires_at=1234567890,
        offer_address="EQCG_offer_address",
    ),
    raw.types.WalletOnchainGiftActionOfferCreate(
        offer_address="EQCG_offer_address",
        price=100,
        amount=1,
        service_fee=5,
        counterparty_address="EQCG_counterparty_address",
        expires_at=1234567890,
    ),
    raw.types.DraftMessage(
        message="hello",
        date=0,
        ai_style=raw.types.InputAiComposeStyle(emojify=True),
    ),
    raw.types.updates.Difference(
        new_messages=[],
        new_encrypted_messages=[],
        other_updates=[],
        chats=[],
        users=[],
        state=raw.types.updates.State(
            pts=1, qts=0, date=0, seq=0, unread_count=0
        ),
        topics=[forum_topic()],
    ),
    raw.types.messages.Dialogs(
        dialogs=[],
        messages=[],
        chats=[],
        users=[],
        topics=[forum_topic()],
    ),
    raw.types.UpdateChannelTooLong(
        channel_id=1,
        pts=10,
        last_msg_id=5,
        last_msg_date=1234567890,
    ),
    raw.functions.aicompose.SetChatStyle(
        peer=raw.types.InputPeerChannel(channel_id=1, access_hash=0),
        style=raw.types.InputAiComposeStyle(proofread=True),
    ),
    raw.functions.messages.InviteUsersToBot(
        bot=raw.types.InputUser(user_id=1, access_hash=0),
        users=[raw.types.InputUser(user_id=2, access_hash=0)],
    ),
    raw.functions.messages.GetForumTopics(
        peer=raw.types.InputPeerChannel(channel_id=1, access_hash=0),
        offset_date=0,
        offset_id=0,
        offset_topic=0,
        limit=100,
        icon_emoji_id=123,
        closed=True,
    ),
    raw.functions.payments.BuyStarGiftOnchain(
        slug="gift-1",
        expected_amount=100,
        show_name=True,
    ),
    raw.functions.messages.GetTranscriptionModels(version=1),
])
def test_layer_234_wire_roundtrip(value):
    assert layer == 235
    encoded = value.write()
    buffer = BytesIO(encoded)
    decoded = TLObject.read(buffer)
    assert type(decoded) is type(value)
    assert decoded.write() == encoded
    assert buffer.tell() == len(encoded)


def test_get_share_theme_removed_from_schema():
    # Layer 234 dropped messages.getShareTheme; the theme now comes with
    # channelFull/userFull instead.
    assert not hasattr(raw.functions.messages, "GetShareTheme")
    assert "share_theme" in raw.types.ChannelFull.__slots__
    assert "share_theme" in raw.types.UserFull.__slots__


def test_share_theme_parse_none_is_default():
    result = types.ShareTheme._parse(None)

    assert result.gift is None
    assert result.backdrop_id is None
    assert result.emojis is None


def test_get_share_theme_reads_full_chat():
    import asyncio

    from pyrogram.methods.messages.get_share_theme import GetShareTheme

    class ShareThemeClient(GetShareTheme):
        def __init__(self, result):
            self.result = result
            self.rpc = None

        async def invoke(self, rpc):
            self.rpc = rpc
            return self.result

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerChannel(channel_id=1, access_hash=0)

    full = raw.types.messages.ChatFull(
        full_chat=raw.types.ChannelFull(
            id=1,
            about="",
            chat_photo=raw.types.ChatPhotoEmpty(),
            notify_settings=raw.types.PeerNotifySettings(),
            read_inbox_max_id=0,
            read_outbox_max_id=0,
            unread_count=0,
            bot_info=[],
            pts=0,
            share_theme=raw.types.ShareThemeEmojiBackdrop(backdrop_id=3),
        ),
        chats=[],
        users=[],
    )
    client = ShareThemeClient(full)

    theme = asyncio.run(GetShareTheme.get_share_theme(client, "news"))

    assert isinstance(client.rpc, raw.functions.channels.GetFullChannel)
    assert theme.backdrop_id == 3
