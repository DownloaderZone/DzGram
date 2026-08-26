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
from pyrogram import raw, types
from ..object import Object


class RichTextButton(Object):
    """This object represents a button reference in rich text.

    Parameters:
        button (:obj:`~pyrogram.types.RichMessageButton`):
            The button.
    """

    def __init__(self, *, button: "types.RichMessageButton"):
        super().__init__()

        self.button = button

    @staticmethod
    def read(button: "raw.types.RichTextButton"):
        return RichTextButton(
            button=types.RichMessageButton.read(button.button),
        )

    async def write(self, client: "pyrogram.Client"):
        return raw.types.RichTextButton(
            button=await self.button.write(client),
        )
