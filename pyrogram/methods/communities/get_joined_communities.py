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

from typing import List

import pyrogram
from pyrogram import raw, types


class GetJoinedCommunities:
    async def get_joined_communities(
        self: "pyrogram.Client",
    ) -> List["types.Chat"]:
        """Get the communities you are a member of.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.Chat`: The joined communities.

        Example:
            .. code-block:: python

                communities = await app.get_joined_communities()
                for community in communities:
                    print(community.title)
        """
        result = await self.invoke(
            raw.functions.communities.GetJoinedCommunities()
        )

        return types.List(
            [
                types.Chat._parse_chat(self, chat)
                for chat in result.chats
            ]
        )
