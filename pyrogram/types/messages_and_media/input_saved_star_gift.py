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

from typing import Optional, Union

import pyrogram
from pyrogram import raw
from ..object import Object


class InputSavedStarGift(Object):
    """Identifier of a saved star gift.

    Exactly one of *user_message_id*, *chat_id*/*saved_id* or *slug* must be provided.

    Parameters:
        user_message_id (``int``, *optional*):
            Identifier of the message containing the gift in a private chat.

        chat_id (``int`` | ``str``, *optional*):
            Identifier of the chat containing the gift.

        saved_id (``int``, *optional*):
            Identifier of the gift in the chat.

        slug (``str``, *optional*):
            Unique gift slug.
    """

    def __init__(
        self,
        *,
        user_message_id: Optional[int] = None,
        chat_id: Optional[Union[int, str]] = None,
        saved_id: Optional[int] = None,
        slug: Optional[str] = None,
    ):
        super().__init__()

        self.user_message_id = user_message_id
        self.chat_id = chat_id
        self.saved_id = saved_id
        self.slug = slug

    async def write(self, client: "pyrogram.Client") -> "raw.base.InputSavedStarGift":
        if self.slug is not None:
            return raw.types.InputSavedStarGiftSlug(slug=self.slug)

        if self.chat_id is not None:
            if self.saved_id is None:
                raise ValueError("saved_id is required when chat_id is used")

            return raw.types.InputSavedStarGiftChat(
                peer=await client.resolve_peer(self.chat_id),
                saved_id=self.saved_id,
            )

        if self.user_message_id is not None:
            return raw.types.InputSavedStarGiftUser(msg_id=self.user_message_id)

        raise ValueError("You must provide user_message_id, chat_id/saved_id or slug")
