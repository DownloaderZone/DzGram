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
from pyrogram import raw


class SetInterestCategories:
    async def set_interest_categories(
        self: "pyrogram.Client",
        category_ids: List[int],
    ) -> bool:
        """Set the interest categories used by the feed.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            category_ids (List of ``int``):
                Identifiers of the selected categories.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_interest_categories([1, 2, 3])
        """
        return await self.invoke(
            raw.functions.feed.SetInterestCategories(
                category_ids=category_ids
            )
        )
