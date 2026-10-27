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

from pyrogram import raw, types
from ..object import Object


class InterestCategories(Object):
    """Interest categories available for the feed.

    Parameters:
        categories (List of :obj:`~pyrogram.types.InterestCategory`):
            Available categories.

        selected (List of ``int``):
            Identifiers of the selected categories.
    """

    def __init__(
        self,
        *,
        categories: List["types.InterestCategory"],
        selected: List[int],
    ):
        super().__init__()

        self.categories = categories
        self.selected = selected

    @staticmethod
    def _parse(result: "raw.base.feed.InterestCategories") -> "InterestCategories":
        if isinstance(result, raw.types.feed.InterestCategoriesNotModified):
            return InterestCategories(categories=types.List(), selected=[])

        return InterestCategories(
            categories=types.List(
                [
                    types.InterestCategory._parse(category)
                    for category in result.categories
                ]
            ),
            selected=list(result.selected),
        )
