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


class ToggleCommunityPeerLink:
    async def toggle_community_peer_link(
        self: "pyrogram.Client",
        community_id: Union[int, str],
        peer_id: Union[int, str],
        visible: bool = False,
        hidden: bool = False,
        deleted: bool = False,
    ) -> bool:
        """Link or unlink a peer to a community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Identifier of the community.

            peer_id (``int`` | ``str``):
                Identifier of the peer.

            visible (``bool``, *optional*):
                Whether the peer should be visible in the community.

            hidden (``bool``, *optional*):
                Whether the peer link should be hidden.

            deleted (``bool``, *optional*):
                Pass True to remove the link.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.toggle_community_peer_link(community_id, peer_id)
        """
        return await self.invoke(
            raw.functions.communities.TogglePeerLink(
                visible=visible,
                hidden=hidden,
                deleted=deleted,
                community=await utils.get_input_channel(self, community_id),
                peer=await self.resolve_peer(peer_id),
            )
        )
