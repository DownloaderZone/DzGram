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

from typing import Union

import pyrogram
from pyrogram import raw, types


class GetAvailableGifts:
    async def get_available_gifts(
        self: "pyrogram.Client",
    ) -> list[Union["types.Gift", "types.UpgradedGift"]]:
        """Get all gifts that can be sent to other users.

        .. include:: /_includes/usable-by/users-bots.rst

        Returns:
            List of :obj:`~pyrogram.types.Gift` | :obj:`~pyrogram.types.UpgradedGift`: On success, a list of star gifts that can be sent by the Client to users and channel chats is returned.

        Example:
            .. code-block:: python

                app.get_available_gifts()
        """
        r = await self.invoke(
            raw.functions.payments.GetStarGifts(hash=0)
        )

        return types.List([
            await types.Gift._parse(self, gift, {})
            for gift in r.gifts
        ])
