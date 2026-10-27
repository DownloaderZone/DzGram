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

from typing import Optional, Union

import pyrogram
from pyrogram import raw


class DisplayStarGift:
    async def display_star_gift(
        self: "pyrogram.Client",
        slug: str,
        chat_id: Optional[Union[int, str]] = None,
    ) -> bool:
        """Display a star gift on a profile.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            slug (``str``):
                Unique slug of the gift.

            chat_id (``int`` | ``str``, *optional*):
                Identifier of the chat whose profile should display the gift.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.display_star_gift("gift-slug")
        """
        return await self.invoke(
            raw.functions.payments.DisplayStarGift(
                peer=await self.resolve_peer(chat_id) if chat_id is not None else None,
                slug=slug,
            )
        )
