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
from pyrogram import raw, types


class ExportNoPaidMessagesToken:
    async def export_no_paid_messages_token(
        self: "pyrogram.Client",
        revoke: bool = False,
        temporary: bool = False,
    ) -> "types.ExportedNoPaidMessagesToken":
        """Export a token that allows users to send you messages without paying.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            revoke (``bool``, *optional*):
                Revoke the current token before exporting a new one.

            temporary (``bool``, *optional*):
                Whether the token should expire.

        Returns:
            :obj:`~pyrogram.types.ExportedNoPaidMessagesToken`: The exported token.

        Example:
            .. code-block:: python

                token = await app.export_no_paid_messages_token()
                print(token.url)
        """
        result = await self.invoke(
            raw.functions.contacts.ExportNoPaidMessagesToken(
                revoke=revoke,
                temporary=temporary,
            )
        )

        return types.ExportedNoPaidMessagesToken._parse(result)
