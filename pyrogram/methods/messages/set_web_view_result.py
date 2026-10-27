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

import pyrogram
from pyrogram import raw


class SetWebViewResult:
    async def set_web_view_result(
        self: "pyrogram.Client",
        query_id: int,
        result: "raw.base.InputBotInlineResult",
    ) -> bool:
        """Set the result of a web view.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            query_id (``int``):
                The web view query identifier.

            result (:obj:`~pyrogram.raw.base.InputBotInlineResult`):
                The result to set.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_web_view_result(query_id, result)
        """
        return await self.invoke(
            raw.functions.messages.SetWebViewResult(
                query_id=query_id,
                result=result,
            )
        )
