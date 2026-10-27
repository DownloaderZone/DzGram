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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types


class CreateCommunity:
    async def create_community(
        self: "pyrogram.Client",
        title: str,
        peer_id: Union[int, str],
        about: Optional[str] = None,
        hidden: bool = False,
    ) -> "types.Chat":
        """Create a new community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            title (``str``):
                Community title.

            peer_id (``int`` | ``str``):
                Identifier of the peer that will own the community.

            about (``str``, *optional*):
                Community description.

            hidden (``bool``, *optional*):
                Whether the community should be hidden.

        Returns:
            :obj:`~pyrogram.types.Chat`: On success, the created community is returned.

        Example:
            .. code-block:: python

                community = await app.create_community("My Community", "me")
        """
        result = await self.invoke(
            raw.functions.communities.Create(
                title=title,
                about=about,
                peer=await self.resolve_peer(peer_id),
                hidden=hidden,
            )
        )

        return types.Chat._parse_chat(self, result.chats[0])
