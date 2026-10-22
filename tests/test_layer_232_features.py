import asyncio
from io import BytesIO

from pyrogram import enums, raw, types
from pyrogram.raw.core import TLObject


class FakeClient:
    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=1)


def run(coro):
    return asyncio.run(coro)


def test_message_generation_stopped_from_typing_update():
    update = raw.types.UpdateUserTyping(
        user_id=5,
        top_msg_id=3,
        action=raw.types.SendMessageStopDraftAction(random_id=7),
    )
    users = {
        5: raw.types.User(
            id=5,
            access_hash=1,
            first_name="A",
            usernames=[],
            restriction_reason=[],
        )
    }

    result = run(
        types.MessageGenerationStopped._parse(
            FakeClient(), update, users, {}
        )
    )

    assert result.chat.id == 5
    assert result.draft_id == 7
    assert result.message_thread_id == 3


def test_community_chat_joined():
    community = raw.types.Community(
        id=99,
        title="Community",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
    )
    action = raw.types.MessageActionChatJoinedViaCommunity(community_id=99)

    result = types.CommunityChatJoined._parse(
        FakeClient(), action, {}, {99: community}
    )

    assert result.chat.id == -1000000000099
    assert result.chat.title == "Community"
    assert result.chat.type == enums.ChatType.COMMUNITY


def test_rich_block_button_row():
    result = run(
        types.RichBlock._parse(
            FakeClient(),
            raw.types.PageBlockButtonRow(buttons=[], align_right=True),
        )
    )

    assert isinstance(result, types.RichBlockButtonRow)
    assert result.alignment == 2


def test_rich_block_collapsed_quote():
    result = run(
        types.RichBlock._parse(
            FakeClient(),
            raw.types.PageBlockBlockquote(
                collapsed=True,
                text=raw.types.TextPlain(text="x"),
                caption=raw.types.TextPlain(text="c"),
            ),
        )
    )

    assert isinstance(result, types.RichBlockBlockQuotation)
    assert result.is_expandable is True


def test_real_rich_input_blocks_roundtrip():
    for block in (
        types.InputRichBlockButtonRow([], 1),
        types.InputRichBlockCollapsedBlockQuotation("text", "caption", True),
        types.InputRichBlockDocument(5),
    ):
        raw_block = block.write()
        assert isinstance(raw_block, TLObject)
        assert TLObject.read(BytesIO(raw_block.write())).write() == raw_block.write()
