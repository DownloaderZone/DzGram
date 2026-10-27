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


class GetInterestCategories:
    async def get_interest_categories(
        self: "pyrogram.Client",
        hash: int = 0,
    ) -> "types.InterestCategories":
        """Get the interest categories available for the feed.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hash (``int``, *optional*):
                Hash of the previously fetched list.

        Returns:
            :obj:`~pyrogram.types.InterestCategories`: The interest categories.

        Example:
            .. code-block:: python

                categories = await app.get_interest_categories()
        """
        return types.InterestCategories._parse(
            await self.invoke(
                raw.functions.feed.GetInterestCategories(
                    hash=hash
                )
            )
        )
