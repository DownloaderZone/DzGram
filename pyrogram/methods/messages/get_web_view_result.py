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
from pyrogram import raw, types, utils


class GetWebViewResult:
    async def get_web_view_result(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        bot_id: Union[int, str],
        query_id: int,
    ) -> "types.WebViewResult":
        """Get the result of a web view.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Identifier of the chat where the web view was opened.

            bot_id (``int`` | ``str``):
                Identifier of the bot that owns the web view.

            query_id (``int``):
                The web view query identifier.

        Returns:
            :obj:`~pyrogram.types.WebViewResult`: The web view result.

        Example:
            .. code-block:: python

                result = await app.get_web_view_result(chat_id, bot_id, query_id)
        """
        r = await self.invoke(
            raw.functions.messages.GetWebViewResult(
                peer=await self.resolve_peer(chat_id),
                bot=await utils.get_input_user(self, bot_id),
                query_id=query_id,
            )
        )

        return types.WebViewResult._parse(self, r)
