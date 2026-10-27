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
from pyrogram import raw, types, utils


class ImportNoPaidMessagesToken:
    async def import_no_paid_messages_token(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        token: str,
    ) -> "types.User":
        """Import a token that allows sending messages to a user without paying.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Identifier of the user the token belongs to.

            token (``str``):
                The token to import.

        Returns:
            :obj:`~pyrogram.types.User`: The user.

        Example:
            .. code-block:: python

                user = await app.import_no_paid_messages_token(123456789, token)
        """
        result = await self.invoke(
            raw.functions.contacts.ImportNoPaidMessagesToken(
                user_id=await utils.get_input_user(self, user_id),
                token=token,
            )
        )

        return types.User._parse(self, result)
