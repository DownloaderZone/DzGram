import asyncio
from io import BytesIO

import pytest

from pyrogram import raw, types
from pyrogram.methods.bots import GetBotFullInfo, GetMySettings, SetMySettings
from pyrogram.raw.all import layer
from pyrogram.raw.core import TLObject


def run(coro):
    return asyncio.run(coro)


def make_settings(**kwargs):
    return raw.types.bots.BotSettings(**kwargs)


def test_layer_is_accepted_by_telegram():
    # Telegram production currently rejects layer 235 with CONNECTION_LAYER_INVALID;
    # the Bot API 10.5 constructors ship under the last accepted layer number.
    assert layer == 234


def test_105_constructors_exist():
    assert hasattr(raw.types.bots, "BotSettings")
    assert hasattr(raw.types.bots, "BotFullInfo")
    assert hasattr(raw.functions.bots, "SetMySettings")
    assert hasattr(raw.functions.bots, "GetMySettings")
    assert hasattr(raw.functions.bots, "GetFullInfo")


@pytest.mark.parametrize(
    "value",
    [
        make_settings(inline_mode=True),
        make_settings(
            inline_mode=True,
            privacy_mode=True,
            can_join_groups=True,
            forum_topic_mode=True,
            callback_query_inline=True,
            has_topic_sidebar=True,
        ),
        make_settings(has_topic_sidebar=True),
        raw.types.bots.BotFullInfo(
            active_usernames=["dog", "dogbot"],
            inline_query_placeholder="search...",
            needs_inline_query_location=True,
            has_topic_sidebar=True,
            settings=make_settings(inline_mode=True),
        ),
        raw.types.bots.BotFullInfo(settings=make_settings(privacy_mode=True)),
    ],
)
def test_105_wire_roundtrip(value):
    encoded = value.write()
    buffer = BytesIO(encoded)
    decoded = TLObject.read(buffer)
    assert type(decoded) is type(value)
    assert decoded.write() == encoded
    assert buffer.tell() == len(encoded)


def test_constructor_ids_match_schema():
    assert raw.types.bots.BotSettings.ID == 0xF7389ABB
    assert raw.types.bots.BotFullInfo.ID == 0xE2023DF2
    assert raw.functions.bots.SetMySettings.ID == 0xE70961C4
    assert raw.functions.bots.GetMySettings.ID == 0x3B08776C
    assert raw.functions.bots.GetFullInfo.ID == 0xE59BDFBD


def test_high_level_settings_write_roundtrip():
    settings = types.BotSettings(
        inline_mode=True,
        privacy_mode=False,
        can_join_groups=True,
    )
    parsed = types.BotSettings._parse(settings.write())
    assert parsed.inline_mode is True
    assert parsed.can_join_groups is True
    # False is not transmitted: the flag is simply absent on the wire.
    assert parsed.privacy_mode is None


def test_high_level_full_info_parse():
    full_info = types.BotFullInfo._parse(
        raw.types.bots.BotFullInfo(
            active_usernames=["dog"],
            inline_query_placeholder="search...",
            needs_inline_query_location=True,
            has_topic_sidebar=True,
            settings=make_settings(inline_mode=True),
        )
    )
    assert full_info.active_usernames == ["dog"]
    assert full_info.inline_query_placeholder == "search..."
    assert full_info.needs_inline_query_location is True
    assert full_info.has_topic_sidebar is True
    assert full_info.settings.inline_mode is True

    empty = types.BotFullInfo._parse(raw.types.bots.BotFullInfo())
    assert empty.active_usernames is None
    assert empty.settings is None


class InvokeRecorder(SetMySettings, GetMySettings, GetBotFullInfo):
    def __init__(self):
        self.rpc = None

    async def invoke(self, rpc, *args, **kwargs):
        self.rpc = rpc
        if isinstance(rpc, raw.functions.bots.GetMySettings):
            return make_settings(inline_mode=True, can_join_groups=True)
        if isinstance(rpc, raw.functions.bots.GetFullInfo):
            return raw.types.bots.BotFullInfo(
                active_usernames=["dog"],
                settings=make_settings(inline_mode=True),
            )
        return True


def test_wrappers_send_expected_raw_calls():
    client = InvokeRecorder()

    assert run(client.set_my_settings(inline_mode=True, can_join_groups=False))
    assert isinstance(client.rpc, raw.functions.bots.SetMySettings)
    sent = client.rpc.settings
    assert sent.inline_mode is True
    # A False flag is not expressible on the wire: it is simply absent.
    assert sent.can_join_groups is None

    settings = run(client.get_my_settings())
    assert isinstance(client.rpc, raw.functions.bots.GetMySettings)
    assert isinstance(settings, types.BotSettings)
    assert settings.inline_mode is True
    assert settings.can_join_groups is True

    full_info = run(client.get_bot_full_info())
    assert isinstance(client.rpc, raw.functions.bots.GetFullInfo)
    assert isinstance(full_info, types.BotFullInfo)
    assert full_info.active_usernames == ["dog"]
    assert full_info.settings.inline_mode is True
