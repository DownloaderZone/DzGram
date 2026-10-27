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

from datetime import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, utils
from ..object import Object


class CommunityPeerRequest(Object):
    """A request to link a peer to a community.

    Parameters:
        peer_id (``int``):
            Identifier of the peer.

        requested_by (``int``):
            Identifier of the user who requested the link.

        date (:py:obj:`~datetime.datetime`):
            Date when the request was created.

        visible (``bool``, *optional*):
            Whether the peer is visible in the community.
    """

    def __init__(
        self,
        *,
        peer_id: int,
        requested_by: int,
        date: datetime,
        visible: Optional[bool] = None,
    ):
        super().__init__()

        self.peer_id = peer_id
        self.requested_by = requested_by
        self.date = date
        self.visible = visible

    @staticmethod
    def _parse(request: "raw.types.CommunityPeerRequest") -> "CommunityPeerRequest":
        return CommunityPeerRequest(
            peer_id=utils.get_peer_id(request.peer),
            requested_by=request.requested_by,
            date=utils.timestamp_to_datetime(request.date),
            visible=request.visible or None,
        )
