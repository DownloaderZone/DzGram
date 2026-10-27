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

import pyrogram
from pyrogram import raw, types, utils
from ..object import Object


class FeedPosition(Object):
    """A position inside the feed.

    Parameters:
        date (``int``):
            Date of the position.

        peer (:obj:`~pyrogram.types.Chat` | :obj:`~pyrogram.types.User`, *optional*):
            Peer of the position.

        id (``int``):
            Identifier of the position.
    """

    def __init__(
        self,
        *,
        date: int,
        peer=None,
        id: int,
    ):
        super().__init__()

        self.date = date
        self.peer = peer
        self.id = id

    def write(self) -> "raw.types.FeedPosition":
        raw_position = getattr(self, "_raw", None)

        if raw_position is not None:
            return raw_position

        peer = None

        if self.peer is not None:
            from pyrogram import utils

            peer_id = self.peer.id

            if peer_id > 0:
                peer = raw.types.PeerUser(user_id=peer_id)
            elif peer_id < -1000000000000:
                peer = raw.types.PeerChannel(channel_id=utils.get_channel_id(peer_id))
            else:
                peer = raw.types.PeerChat(chat_id=-peer_id)

        return raw.types.FeedPosition(
            date=self.date,
            peer=peer,
            id=self.id,
        )

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        position: "raw.base.FeedPosition",
        users: dict = None,
        chats: dict = None,
    ):
        if position is None:
            return None

        users = users or {}
        chats = chats or {}

        peer = None
        peer_id = utils.get_raw_peer_id(position.peer)

        if utils.get_peer_type(utils.get_peer_id(position.peer)) == "user":
            raw_user = users.get(peer_id)
            if raw_user is not None:
                peer = types.User._parse(client, raw_user)
        else:
            raw_chat = chats.get(peer_id)
            if raw_chat is not None:
                peer = types.Chat._parse_chat(client, raw_chat)

        result = FeedPosition(
            date=position.date,
            peer=peer,
            id=position.id,
        )
        result._raw = position
        return result
