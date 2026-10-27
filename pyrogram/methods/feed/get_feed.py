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

from typing import Optional

import pyrogram
from pyrogram import raw, types


class GetFeed:
    async def get_feed(
        self: "pyrogram.Client",
        filter_id: int = 0,
        offset_position: Optional["types.FeedPosition"] = None,
        add_offset: int = 0,
        limit: int = 20,
        max_position: Optional["types.FeedPosition"] = None,
        min_position: Optional["types.FeedPosition"] = None,
        hash: int = 0,
        offset_to_max_read: bool = False,
    ) -> "types.FeedMessages":
        """Get messages from the feed.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            filter_id (``int``, *optional*):
                Identifier of the feed filter. Defaults to 0 (all).

            offset_position (:obj:`~pyrogram.types.FeedPosition`, *optional*):
                Offset position.

            add_offset (``int``, *optional*):
                Additional offset.

            limit (``int``, *optional*):
                Maximum number of messages to return. Defaults to 20.

            max_position (:obj:`~pyrogram.types.FeedPosition`, *optional*):
                Maximum position.

            min_position (:obj:`~pyrogram.types.FeedPosition`, *optional*):
                Minimum position.

            hash (``int``, *optional*):
                Hash of the previously fetched feed.

            offset_to_max_read (``bool``, *optional*):
                Pass True to offset to the maximum read position.

        Returns:
            :obj:`~pyrogram.types.FeedMessages`: The feed messages.

        Example:
            .. code-block:: python

                feed = await app.get_feed(limit=50)
        """
        return await types.FeedMessages._parse(
            self,
            await self.invoke(
                raw.functions.feed.GetFeed(
                    filter_id=filter_id,
                    offset_position=offset_position.write() if offset_position else None,
                    add_offset=add_offset,
                    limit=limit,
                    max_position=max_position.write() if max_position else None,
                    min_position=min_position.write() if min_position else None,
                    hash=hash,
                    offset_to_max_read=offset_to_max_read or None,
                )
            ),
        )
