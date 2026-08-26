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

from typing import Dict

import pyrogram
from pyrogram import raw, types
from ..object import Object


class CommunityChatJoined(Object):
    """This object represents a service message about a community chat being joined.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            The chat that was joined.
    """

    def __init__(self, *, chat: "types.Chat"):
        super().__init__()

        self.chat = chat

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        action: "raw.types.MessageActionChatJoinedByRequest",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {},
    ) -> "CommunityChatJoined":
        return CommunityChatJoined(
            chat=types.Chat._parse_chat(client, chats[action.chat_id]) if action.chat_id in chats else None,
        )
