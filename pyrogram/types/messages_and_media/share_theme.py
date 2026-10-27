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

from typing import List, Optional

import pyrogram
from pyrogram import raw, types
from ..object import Object


class ShareTheme(Object):
    """A theme used when sharing a chat.

    Exactly one of *gift*, *backdrop_id* or *emojis* may be provided. If none is
    provided, the default share theme is used.

    Parameters:
        gift (:obj:`~pyrogram.types.InputSavedStarGift`, *optional*):
            Star gift to use as the theme.

        backdrop_id (``int``, *optional*):
            Identifier of the backdrop to use.

        emojis (List of :obj:`~pyrogram.raw.base.Reaction`, *optional*):
            Emoji reactions to use as the theme.
    """

    def __init__(
        self,
        *,
        gift: Optional["types.InputSavedStarGift"] = None,
        backdrop_id: Optional[int] = None,
        emojis: Optional[List["raw.base.Reaction"]] = None,
    ):
        super().__init__()

        self.gift = gift
        self.backdrop_id = backdrop_id
        self.emojis = emojis

    @staticmethod
    def _parse(theme: "raw.base.ShareTheme") -> "ShareTheme":
        if isinstance(theme, raw.types.ShareThemeGift):
            return ShareTheme(gift=theme.stargift)
        if isinstance(theme, raw.types.ShareThemeEmojiBackdrop):
            return ShareTheme(backdrop_id=theme.backdrop_id, emojis=theme.emojis)
        return ShareTheme()

    async def write(self, client: "pyrogram.Client") -> "raw.base.ShareTheme":
        if self.gift is not None:
            return raw.types.InputShareThemeGift(
                stargift=await self.gift.write(client)
            )

        if self.backdrop_id is not None or self.emojis is not None:
            return raw.types.ShareThemeEmojiBackdrop(
                backdrop_id=self.backdrop_id,
                emojis=self.emojis,
            )

        return raw.types.ShareThemeDefault()
