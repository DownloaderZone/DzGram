import asyncio
from io import BytesIO

import pytest

from pyrogram import Client, raw, types, utils
from pyrogram.methods.chats.join_chat import JoinChat


def run(coro):
    return asyncio.run(coro)


class JoinChatClient(JoinChat):
    INVITE_LINK_RE = Client.INVITE_LINK_RE
    TME_PUBLIC_LINK_RE = Client.TME_PUBLIC_LINK_RE

    def __init__(self, result):
        self.result = result
        self.rpc = None

    async def invoke(self, rpc):
        self.rpc = rpc
        return self.result

    async def resolve_peer(self, chat_id):
        return raw.types.InputPeerChannel(channel_id=1, access_hash=0)

    async def get_chat(self, chat_id):
        raise AssertionError("the chat should be taken from the join result")


def test_prepare_photo_upload_renames_jpe(tmp_path):
    photo = tmp_path / "poster_b5848fb5.jpe"
    photo.write_bytes(b"\xff\xd8\xff\xe0" + b"0" * 32)

    prepared = utils.prepare_photo_upload(str(photo))

    assert prepared.name == "photo.jpg"
    assert prepared.getvalue() == photo.read_bytes()


def test_prepare_photo_upload_fixes_mismatched_extension(tmp_path):
    photo = tmp_path / "photo.jpg"
    photo.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)

    prepared = utils.prepare_photo_upload(str(photo))

    assert prepared.name == "photo.png"
    assert prepared.getvalue() == photo.read_bytes()


def test_prepare_photo_upload_keeps_jpg(tmp_path):
    photo = tmp_path / "photo.jpg"
    photo.write_bytes(b"\xff\xd8\xff\xe0" + b"0" * 32)

    assert utils.prepare_photo_upload(str(photo)) == str(photo)


def test_prepare_photo_upload_names_unnamed_bytes_io():
    stream = BytesIO(b"\xff\xd8\xff\xe0" + b"0" * 32)

    prepared = utils.prepare_photo_upload(stream)

    assert prepared.name == "photo.jpg"
    assert prepared.getvalue() == stream.getvalue()


def test_prepare_photo_upload_rejects_text(tmp_path):
    document = tmp_path / "YIFYStatus.com.txt"
    document.write_text("not a photo")

    try:
        utils.prepare_photo_upload(str(document))
    except ValueError as e:
        assert "not a valid photo" in str(e)
    else:
        raise AssertionError("a text file must not be accepted as a photo")


def test_prepare_photo_upload_transcodes_gif(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image

    photo = tmp_path / "animation.gif"
    frames = [Image.new("RGB", (32, 32), (i * 60, 40, 80)) for i in range(2)]
    frames[0].save(photo, format="GIF", save_all=True, append_images=frames[1:])

    prepared = utils.prepare_photo_upload(str(photo))

    assert prepared.name == "photo.jpg"
    prepared.seek(0)
    with Image.open(prepared) as image:
        assert image.format == "JPEG"


def test_prepare_photo_upload_reencodes_heavy_png(tmp_path):
    pytest.importorskip("PIL")
    import os

    from PIL import Image

    photo = tmp_path / "screenshot.png"
    Image.frombytes("RGB", (1200, 1200), os.urandom(1200 * 1200 * 3)).save(photo)
    assert photo.stat().st_size > 2 * 1024 * 1024

    prepared = utils.prepare_photo_upload(str(photo))

    assert prepared.name == "photo.jpg"
    prepared.seek(0)
    with Image.open(prepared) as image:
        assert image.format == "JPEG"


def test_feed_messages_parse_empty():
    result = run(
        types.FeedMessages._parse(
            object(),
            raw.types.feed.FeedMessages(
                messages=[],
                chats=[],
                users=[],
            ),
        )
    )

    assert result.messages == []
    assert result.max_position is None


def test_interest_categories_parse():
    result = types.InterestCategories._parse(
        raw.types.feed.InterestCategories(
            categories=[
                raw.types.feed.InterestCategory(id=1, title="Tech", emoji="💻")
            ],
            selected=[1],
        )
    )

    assert result.selected == [1]
    assert result.categories[0].title == "Tech"


def test_agent_providers_parse_not_modified():
    result = types.AgentProviders._parse(
        raw.types.agent.ProvidersNotModified()
    )

    assert result.providers == []


def test_agent_settings_parse():
    result = types.AgentSettings._parse(
        raw.types.agent.Settings(
            keys=[
                raw.types.agent.ProviderKey(
                    provider="openai",
                    key_last4="1234",
                    date_connected=1,
                )
            ],
            active_provider="openai",
        )
    )

    assert result.active_provider == "openai"
    assert result.keys[0].key_last4 == "1234"


def test_share_theme_parse_default():
    result = types.ShareTheme._parse(raw.types.ShareThemeDefault())

    assert result.gift is None
    assert result.backdrop_id is None


def test_join_chat_parses_chat_invite_join_result():
    channel = raw.types.Channel(
        id=1,
        title="News",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        broadcast=True,
        access_hash=123,
    )
    result = raw.types.messages.ChatInviteJoinResultOk(
        updates=raw.types.Updates(
            updates=[],
            users=[],
            chats=[channel],
            date=0,
            seq=0,
        )
    )
    client = JoinChatClient(result)

    chat = run(JoinChat.join_chat(client, "news", for_news=True))

    assert chat.id == utils.get_channel_id(1)
    assert chat.title == "News"
    assert isinstance(client.rpc, raw.functions.channels.JoinChannel)
    assert client.rpc.for_news is True


def test_join_chat_reports_guard_bot_web_view():
    bot = raw.types.User(id=2, first_name="Guard", username="guard_bot")
    result = raw.types.messages.ChatInviteJoinResultWebView(
        bot_id=2,
        query_id=3,
        users=[bot],
    )
    client = JoinChatClient(result)

    try:
        run(JoinChat.join_chat(client, "news"))
    except ValueError as e:
        assert "@guard_bot" in str(e)
    else:
        raise AssertionError("guard bot approval must be reported")


def test_layer_233_methods_exist():
    from pyrogram import Client

    for name in (
        "get_web_view_result",
        "forward_message",
        "edit_inline_bot_message_widget_data",
        "get_widget_public_data",
        "get_share_theme",
        "get_stats_url",
        "get_all_chats",
        "get_bot_widget_query_answer",
        "set_web_view_result",
        "edit_widget_data",
        "edit_message_widget_data",
        "set_bot_widget_query_answer",
        "import_card",
        "edit_channel_news",
        "request_recurring_payment",
        "delete_folder",
        "get_for_you",
        "get_feed",
        "set_interest_categories",
        "read_feed",
        "get_interest_categories",
        "connect_agent",
        "disconnect_agent",
        "get_agent_providers",
        "get_agent_settings",
        "set_agent_active_provider",
    ):
        assert hasattr(Client, name), name
