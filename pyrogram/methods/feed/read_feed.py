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

import pyrogram
from pyrogram import raw, types


class ReadFeed:
    async def read_feed(
        self: "pyrogram.Client",
        max_position: "types.FeedPosition",
        filter_id: int = 0,
    ) -> bool:
        """Mark feed messages as read.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            max_position (:obj:`~pyrogram.types.FeedPosition`):
                Maximum position to mark as read.

            filter_id (``int``, *optional*):
                Identifier of the feed filter. Defaults to 0 (all).

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.read_feed(max_position)
        """
        await self.invoke(
            raw.functions.feed.ReadFeed(
                filter_id=filter_id,
                max_position=max_position.write(),
            )
        )

        return True
