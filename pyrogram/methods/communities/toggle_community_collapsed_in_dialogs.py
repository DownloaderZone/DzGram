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

from typing import Union

import pyrogram
from pyrogram import raw, utils


class ToggleCommunityCollapsedInDialogs:
    async def toggle_community_collapsed_in_dialogs(
        self: "pyrogram.Client",
        community_id: Union[int, str],
        collapsed: bool = True,
    ) -> None:
        """Toggle whether a community is collapsed in the dialog list.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Identifier of the community.

            collapsed (``bool``, *optional*):
                Pass True to collapse the community, False to expand it.

        Example:
            .. code-block:: python

                await app.toggle_community_collapsed_in_dialogs(community_id)
        """
        await self.invoke(
            raw.functions.communities.ToggleCommunityCollapsedInDialogs(
                collapsed=collapsed,
                community=await utils.get_input_channel(self, community_id),
            )
        )
