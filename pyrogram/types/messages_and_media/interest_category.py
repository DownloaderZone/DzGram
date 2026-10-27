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

from pyrogram import raw
from ..object import Object


class InterestCategory(Object):
    """A feed interest category.

    Parameters:
        id (``int``):
            Identifier of the category.

        title (``str``):
            Title of the category.

        emoji (``str``, *optional*):
            Emoji of the category.

        emoji_document_id (``int``, *optional*):
            Identifier of the custom emoji document.
    """

    def __init__(
        self,
        *,
        id: int,
        title: str,
        emoji: Optional[str] = None,
        emoji_document_id: Optional[int] = None,
    ):
        super().__init__()

        self.id = id
        self.title = title
        self.emoji = emoji
        self.emoji_document_id = emoji_document_id

    @staticmethod
    def _parse(category: "raw.types.feed.InterestCategory") -> "InterestCategory":
        return InterestCategory(
            id=category.id,
            title=category.title,
            emoji=getattr(category, "emoji", None),
            emoji_document_id=getattr(category, "emoji_document_id", None),
        )
