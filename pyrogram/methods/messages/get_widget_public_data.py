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


class GetWidgetPublicData:
    async def get_widget_public_data(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        hash: int = 0,
    ) -> "types.WidgetPublicData":
        """Get the public data of a widget.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Identifier of the chat containing the widget message.

            message_id (``int``):
                Identifier of the widget message.

            hash (``int``, *optional*):
                Hash of the previously fetched data. Pass 0 to fetch the data.

        Returns:
            :obj:`~pyrogram.types.WidgetPublicData`: The widget public data.

        Example:
            .. code-block:: python

                data = await app.get_widget_public_data(chat_id, message_id)
        """
        r = await self.invoke(
            raw.functions.messages.GetWidgetPublicData(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                hash=hash,
            )
        )

        return types.WidgetPublicData._parse(r)
