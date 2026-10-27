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

from typing import Optional

import pyrogram
from pyrogram import raw


class SetBotWidgetQueryAnswer:
    async def set_bot_widget_query_answer(
        self: "pyrogram.Client",
        query_id: int,
        result: Optional[str] = None,
    ) -> bool:
        """Set the answer of a bot widget query.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            query_id (``int``):
                The widget query identifier.

            result (``str``, *optional*):
                The answer to send.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_bot_widget_query_answer(query_id, result="{}")
        """
        return await self.invoke(
            raw.functions.messages.SetBotWidgetQueryAnswer(
                query_id=query_id,
                result=result,
            )
        )
