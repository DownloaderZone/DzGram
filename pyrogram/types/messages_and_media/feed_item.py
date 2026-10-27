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

from typing import List

import pyrogram
from pyrogram import raw, types
from ..object import Object


class FeedItem(Object):
    """A single item inside a feed."""

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        item: "raw.base.FeedItem",
        users: dict = None,
        chats: dict = None,
    ):
        users = users or {}
        chats = chats or {}

        if isinstance(item, raw.types.FeedItemMessage):
            return FeedItemMessage(
                message=await types.Message._parse(
                    client, item.message, users, chats
                )
            )

        if isinstance(item, raw.types.FeedItemMessageGroup):
            return FeedItemMessageGroup(
                messages=types.List(
                    [
                        await types.Message._parse(client, message, users, chats)
                        for message in item.messages
                    ]
                )
            )

        if isinstance(item, raw.types.FeedItemInterestCategories):
            return FeedItemInterestCategories()

        return FeedItem()


class FeedItemMessage(FeedItem):
    """A feed item containing a single message.

    Parameters:
        message (:obj:`~pyrogram.types.Message`):
            The message.
    """

    def __init__(self, *, message: "types.Message"):
        super().__init__()

        self.message = message


class FeedItemMessageGroup(FeedItem):
    """A feed item containing a group of messages.

    Parameters:
        messages (List of :obj:`~pyrogram.types.Message`):
            The messages.
    """

    def __init__(self, *, messages: List["types.Message"]):
        super().__init__()

        self.messages = messages


class FeedItemInterestCategories(FeedItem):
    """A placeholder feed item that asks to choose interest categories."""
