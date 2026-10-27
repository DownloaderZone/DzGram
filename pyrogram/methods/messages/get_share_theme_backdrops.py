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

from typing import List

import pyrogram
from pyrogram import raw, types


class GetShareThemeBackdrops:
    async def get_share_theme_backdrops(
        self: "pyrogram.Client",
        hash: int = 0,
    ) -> List["types.ShareThemeBackdrop"]:
        """Get the list of backdrops that can be used for share themes.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hash (``int``, *optional*):
                Hash of the previously fetched list. Pass the hash returned by a
                previous call to get only the changes.

        Returns:
            List of :obj:`~pyrogram.types.ShareThemeBackdrop`: The available backdrops.

        Example:
            .. code-block:: python

                backdrops = await app.get_share_theme_backdrops()
                for backdrop in backdrops:
                    print(backdrop.name)
        """
        result = await self.invoke(
            raw.functions.messages.GetShareThemeBackdrops(hash=hash)
        )

        if isinstance(result, raw.types.ShareThemeBackdropsNotModified):
            return []

        return [
            types.ShareThemeBackdrop._parse(backdrop)
            for backdrop in result.backdrops
        ]
