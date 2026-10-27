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


class ForYouFeed(Object):
    """The personalised "for you" feed.

    Parameters:
        items (List of :obj:`~pyrogram.types.FeedItem`):
            Feed items.
    """

    def __init__(self, *, items: List["types.FeedItem"]):
        super().__init__()

        self.items = items

    @staticmethod
    async def _parse(client: "pyrogram.Client", feed: "raw.types.feed.ForYouFeed") -> "ForYouFeed":
        users = {i.id: i for i in feed.users}
        chats = {i.id: i for i in feed.chats}

        items = []

        for item in feed.items:
            items.append(
                await types.FeedItem._parse(client, item, users, chats)
            )

        return ForYouFeed(items=types.List(items))
