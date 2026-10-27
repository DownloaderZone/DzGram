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

from typing import List, Union

import pyrogram
from pyrogram import raw, types, utils


class GetCommunityParticipantJoinedChats:
    async def get_community_participant_joined_chats(
        self: "pyrogram.Client",
        community_id: Union[int, str],
        user_id: Union[int, str],
    ) -> List["types.Chat"]:
        """Get the community chats a participant has joined.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Identifier of the community.

            user_id (``int`` | ``str``):
                Identifier of the participant.

        Returns:
            List of :obj:`~pyrogram.types.Chat`: The joined chats.

        Example:
            .. code-block:: python

                chats = await app.get_community_participant_joined_chats(community_id, user_id)
                for chat in chats:
                    print(chat.title)
        """
        result = await self.invoke(
            raw.functions.communities.GetParticipantJoinedChats(
                community=await utils.get_input_channel(self, community_id),
                participant=await utils.get_input_user(self, user_id),
            )
        )

        return types.List(
            [
                types.Chat._parse_chat(self, chat)
                for chat in result.chats
            ]
        )
