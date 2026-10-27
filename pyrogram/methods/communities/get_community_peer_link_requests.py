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
from pyrogram import raw, types, utils


class GetCommunityPeerLinkRequests:
    async def get_community_peer_link_requests(
        self: "pyrogram.Client",
        community_id: Union[int, str],
        offset: str = "",
        limit: int = 100,
    ) -> "types.CommunityPeerLinkRequests":
        """Get the pending requests to link peers to a community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Identifier of the community.

            offset (``str``, *optional*):
                Offset of the first request to return.

            limit (``int``, *optional*):
                Maximum number of requests to return.

        Returns:
            :obj:`~pyrogram.types.CommunityPeerLinkRequests`: The requests.

        Example:
            .. code-block:: python

                requests = await app.get_community_peer_link_requests(community_id)
                print(requests.total_count)
        """
        result = await self.invoke(
            raw.functions.communities.GetPeerLinkRequests(
                community=await utils.get_input_channel(self, community_id),
                offset=offset,
                limit=limit,
            )
        )

        return types.CommunityPeerLinkRequests._parse(result)
