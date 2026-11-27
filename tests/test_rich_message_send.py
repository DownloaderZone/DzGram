#  DzGram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present Downloader Zone <https://github.com/DownloaderZone>
#
#  This file is part of DzGram, a fork of Pyrogram.
#
#  DzGram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  DzGram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with DzGram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio

from pyrogram import enums, raw, types
from pyrogram.methods.messages.send_rich_message import SendRichMessage


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


PEER_USER = raw.types.InputPeerUser(user_id=777, access_hash=0)
PEER_CHAT = raw.types.InputPeerChat(chat_id=456)


class Recorder(SendRichMessage):
    def __init__(self, reply, peer=PEER_USER):
        self.reply = reply
        self.peer = peer
        self.rpc = None
        self.fetch_replies = False

    async def resolve_peer(self, chat_id):
        return self.peer

    def rnd_id(self):
        return -4242

    async def invoke(self, rpc, *args, **kwargs):
        self.rpc = rpc
        return self.reply


def updates(items):
    return raw.types.Updates(updates=items, users=[], chats=[], date=0, seq=0)


def short_sent(mid=11, **kwargs):
    return raw.types.UpdateShortSentMessage(id=mid, pts=1, pts_count=1, date=1700000000, **kwargs)


def test_send_rich_message_html_input():
    client = Recorder(short_sent())
    run(client.send_rich_message(-1001234567890, "<b>hello</b>"))
    assert isinstance(client.rpc.rich_message, raw.types.InputRichMessageHTML)
    assert client.rpc.rich_message.html == "<b>hello</b>"
    assert client.rpc.message == ""


def test_send_rich_message_markdown_input():
    client = Recorder(short_sent())
    run(client.send_rich_message(-1001234567890, "**hello**", parse_mode=enums.ParseMode.MARKDOWN))
    assert isinstance(client.rpc.rich_message, raw.types.InputRichMessageMarkdown)
    assert client.rpc.rich_message.markdown == "**hello**"


def test_send_rich_message_short_sent_reply():
    client = Recorder(short_sent(out=True))
    message = run(client.send_rich_message(777, "<b>hello</b>"))
    assert isinstance(message, types.Message)
    assert message.id == 11
    assert message.chat.id == 777


def test_send_rich_message_short_sent_reply_chat_peer():
    client = Recorder(short_sent(mid=12), peer=PEER_CHAT)
    message = run(client.send_rich_message(-1001234567890, "<b>hello</b>"))
    assert message.id == 12
    assert message.chat.id == -456


def test_send_rich_message_new_message_reply():
    client = Recorder(
        updates([raw.types.UpdateNewMessage(message=raw.types.MessageEmpty(id=22), pts=1, pts_count=1)])
    )
    message = run(client.send_rich_message(-1001234567890, "<b>hello</b>"))
    assert message.id == 22
    assert message.empty is True


def test_send_rich_message_scheduled_reply():
    client = Recorder(
        updates([raw.types.UpdateNewScheduledMessage(message=raw.types.MessageEmpty(id=23))])
    )
    message = run(client.send_rich_message(-1001234567890, "<b>hello</b>"))
    assert message.id == 23


def test_send_rich_message_business_reply():
    client = Recorder(
        updates(
            [
                raw.types.UpdateBotNewBusinessMessage(
                    connection_id="bc1",
                    message=raw.types.MessageEmpty(id=24),
                    qts=1,
                )
            ]
        )
    )
    message = run(client.send_rich_message(-1001234567890, "<b>hello</b>"))
    assert message.id == 24
    assert message.business_connection_id == "bc1"
