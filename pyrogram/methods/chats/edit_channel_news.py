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

from typing import Union

import pyrogram
from pyrogram import raw, utils


class EditChannelNews:
    async def edit_channel_news(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        news: bool = True,
    ) -> bool:
        """Enable or disable the news mode of a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Identifier of the channel.

            news (``bool``, *optional*):
                Pass True to enable the news mode, False to disable it.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_channel_news(chat_id, True)
        """
        await self.invoke(
            raw.functions.channels.EditChannelNews(
                channel=await utils.get_input_channel(self, chat_id),
                news=news,
            )
        )

        return True
