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

from typing import List

import pyrogram
from pyrogram import raw, types


class ImportCard:
    async def import_card(
        self: "pyrogram.Client",
        export_card: List[int],
    ) -> "types.User":
        """Import a contact card.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            export_card (List of ``int``):
                The contact card data.

        Returns:
            :obj:`~pyrogram.types.User`: The imported user.

        Example:
            .. code-block:: python

                user = await app.import_card([1, 2, 3])
        """
        return types.User._parse(
            self,
            await self.invoke(
                raw.functions.contacts.ImportCard(
                    export_card=export_card
                )
            )
        )
