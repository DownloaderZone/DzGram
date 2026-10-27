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

from typing import List, Optional

import pyrogram
from pyrogram import raw, types
from ..object import Object


class WebViewResult(Object):
    """The result of a web view.

    Parameters:
        result (:obj:`~pyrogram.raw.base.BotInlineResult`, *optional*):
            The raw inline result.

        users (List of :obj:`~pyrogram.types.User`):
            Users mentioned in the result.
    """

    def __init__(
        self,
        *,
        result: Optional["raw.base.BotInlineResult"] = None,
        users: Optional[List["types.User"]] = None,
    ):
        super().__init__()

        self.result = result
        self.users = users or []

    @staticmethod
    def _parse(client: "pyrogram.Client", web_view: "raw.types.messages.WebViewResult") -> "WebViewResult":
        return WebViewResult(
            result=web_view.result,
            users=types.List(
                [types.User._parse(client, user) for user in web_view.users]
            ),
        )
