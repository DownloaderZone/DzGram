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

import pyrogram
from pyrogram import raw

from ...types import BotFullInfo


class GetBotFullInfo:
    async def get_bot_full_info(
        self: "pyrogram.Client",
    ) -> BotFullInfo:
        """Use this method to get full information about the current bot
        (Bot API 10.5).

        .. include:: /_includes/usable-by/bots.rst

        Raises:
            :obj:`~pyrogram.errors.RPCError`: In case of a Telegram RPC error.

        Returns:
            :obj:`~pyrogram.types.BotFullInfo`: On success, full information
            about the bot is returned.

        Example:
            .. code-block:: python

                full_info = await app.get_bot_full_info()
        """

        return BotFullInfo._parse(
            await self.invoke(raw.functions.bots.GetFullInfo())
        )
