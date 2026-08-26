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

import pyrogram
from pyrogram import raw
from ..object import Object


class MessageGenerationStopped(Object):
    """This object represents a service message that message generation has stopped.

    Parameters:
        chat_id (``int``):
            Chat ID.

        message_id (``int``):
            Message ID.
    """

    def __init__(self, *, chat_id: int, message_id: int):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id

    @staticmethod
    def _parse(update: "raw.types.UpdateMessageGenerationStopped"):
        return MessageGenerationStopped(
            chat_id=update.chat_id,
            message_id=update.message_id,
        )
