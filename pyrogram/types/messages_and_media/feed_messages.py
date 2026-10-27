#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from typing import List, Optional

import pyrogram
from pyrogram import raw, types, utils
from ..object import Object

class FeedMessages(Object):
    """Messages returned by the feed.

    Parameters:
        messages (List of :obj:`~pyrogram.types.Message`):
            The feed messages.

        max_position (:obj:`~pyrogram.types.FeedPosition`, *optional*):
            Maximum position.

        min_position (:obj:`~pyrogram.types.FeedPosition`, *optional*):
            Minimum position.

        read_max_position (:obj:`~pyrogram.types.FeedPosition`, *optional*):
            Maximum read position.
    """

    def __init__(
        self,
        *,
        messages: List["types.Message"],
        max_position: Optional["types.FeedPosition"] = None,
        min_position: Optional["types.FeedPosition"] = None,
        read_max_position: Optional["types.FeedPosition"] = None,
    ):
        super().__init__()

        self.messages = messages
        self.max_position = max_position
        self.min_position = min_position
        self.read_max_position = read_max_position

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        feed: "raw.base.feed.FeedMessages",
    ) -> "FeedMessages":
        if isinstance(feed, raw.types.feed.FeedMessagesNotModified):
            return FeedMessages(messages=types.List())

        users = {i.id: i for i in feed.users}
        chats = {i.id: i for i in feed.chats}

        return FeedMessages(
            messages=await utils.parse_messages(
                client, feed, replies=getattr(client, "fetch_replies", 1)
            ),
            max_position=types.FeedPosition._parse(
                client, getattr(feed, "max_position", None), users, chats
            ),
            min_position=types.FeedPosition._parse(
                client, getattr(feed, "min_position", None), users, chats
            ),
            read_max_position=types.FeedPosition._parse(
                client, getattr(feed, "read_max_position", None), users, chats
            ),
        )
