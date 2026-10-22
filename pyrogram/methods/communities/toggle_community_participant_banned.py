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

from typing import Union

import pyrogram
from pyrogram import raw, utils


class ToggleCommunityParticipantBanned:
    async def toggle_community_participant_banned(
        self: "pyrogram.Client",
        community_id: Union[int, str],
        user_id: Union[int, str],
        unban: bool = False,
    ) -> bool:
        """Ban or unban a participant of a community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Identifier of the community.

            user_id (``int`` | ``str``):
                Identifier of the participant.

            unban (``bool``, *optional*):
                Pass True to unban the participant instead of banning them.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.toggle_community_participant_banned(community_id, user_id)
        """
        return await self.invoke(
            raw.functions.communities.ToggleParticipantBanned(
                unban=unban,
                community=await utils.get_input_channel(self, community_id),
                participant=await utils.get_input_user(self, user_id),
            )
        )
