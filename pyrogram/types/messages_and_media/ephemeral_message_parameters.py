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

from typing import Optional

import pyrogram
from pyrogram import raw
from ..object import Object


class EphemeralMessageParameters(Object):
    """This object represents parameters for ephemeral messages.

    Parameters:
        receiver_user_id (``int``, *optional*):
            Target user ID.

        callback_query_id (``int``, *optional*):
            Callback query ID to replace.

        replace_callback_query_message (``bool``, *optional*):
            Whether to show ephemeral in place of original.
    """

    def __init__(
        self,
        *,
        receiver_user_id: Optional[int] = None,
        callback_query_id: Optional[int] = None,
        replace_callback_query_message: Optional[bool] = None,
    ):
        super().__init__()

        self.receiver_user_id = receiver_user_id
        self.callback_query_id = callback_query_id
        self.replace_callback_query_message = replace_callback_query_message

    @staticmethod
    def read(params: "raw.types.EphemeralMessageParameters"):
        return EphemeralMessageParameters(
            receiver_user_id=params.receiver_user_id,
            callback_query_id=params.callback_query_id,
            replace_callback_query_message=params.replace_callback_query_message or None,
        )

    async def write(self, client: "pyrogram.Client"):
        return raw.types.EphemeralMessageParameters(
            receiver_user_id=self.receiver_user_id,
            callback_query_id=self.callback_query_id,
            replace_callback_query_message=self.replace_callback_query_message or False,
        )
