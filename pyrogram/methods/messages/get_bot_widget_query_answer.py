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


class GetBotWidgetQueryAnswer:
    async def get_bot_widget_query_answer(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        data: bytes,
    ) -> "types.BotWidgetQueryAnswer":
        """Get the answer of a bot widget query.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Identifier of the chat containing the widget message.

            message_id (``int``):
                Identifier of the widget message.

            data (``bytes``):
                Query payload.

        Returns:
            :obj:`~pyrogram.types.BotWidgetQueryAnswer`: The answer.

        Example:
            .. code-block:: python

                answer = await app.get_bot_widget_query_answer(chat_id, message_id, b"data")
        """
        r = await self.invoke(
            raw.functions.messages.GetBotWidgetQueryAnswer(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                data=data,
            )
        )

        return types.BotWidgetQueryAnswer._parse(r)
