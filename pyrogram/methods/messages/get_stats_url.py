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
from pyrogram import raw


class GetStatsUrl:
    async def get_stats_url(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        params: str = "",
        dark: bool = False,
    ) -> str:
        """Get the URL of a chat statistics page.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Identifier of the chat.

            params (``str``, *optional*):
                Additional URL parameters.

            dark (``bool``, *optional*):
                Pass True to get a URL for the dark theme.

        Returns:
            ``str``: The statistics URL.

        Example:
            .. code-block:: python

                url = await app.get_stats_url(chat_id)
        """
        result = await self.invoke(
            raw.functions.messages.GetStatsURL(
                peer=await self.resolve_peer(chat_id),
                params=params,
                dark=dark or None,
            )
        )

        return result.url
