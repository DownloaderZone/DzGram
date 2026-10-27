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

from typing import List, Optional

import pyrogram
from pyrogram import raw, types
from ..object import Object


class CommunityPeerLinkRequests(Object):
    """A list of requests to link peers to a community.

    Parameters:
        total_count (``int``):
            Total number of requests.

        requests (List of :obj:`~pyrogram.types.CommunityPeerRequest`):
            Requests.

        next_offset (``str``, *optional*):
            Offset to use to fetch the next page of requests.
    """

    def __init__(
        self,
        *,
        total_count: int,
        requests: List["types.CommunityPeerRequest"],
        next_offset: Optional[str] = None,
    ):
        super().__init__()

        self.total_count = total_count
        self.requests = requests
        self.next_offset = next_offset

    @staticmethod
    def _parse(
        requests: "raw.types.communities.PeerLinkRequests",
    ) -> "CommunityPeerLinkRequests":
        return CommunityPeerLinkRequests(
            total_count=requests.total_count,
            requests=types.List(
                [
                    types.CommunityPeerRequest._parse(request)
                    for request in requests.requests
                ]
            ),
            next_offset=requests.next_offset,
        )
