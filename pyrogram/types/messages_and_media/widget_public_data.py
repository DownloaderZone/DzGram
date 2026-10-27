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

from pyrogram import raw
from ..object import Object


class WidgetPublicData(Object):
    """Public data of a widget.

    Parameters:
        hash (``int``):
            Hash of the data.

        data (``str``):
            The data.

        period (``int``):
            Cache period.
    """

    def __init__(
        self,
        *,
        hash: int = 0,
        data: str = "",
        period: int = 0,
    ):
        super().__init__()

        self.hash = hash
        self.data = data
        self.period = period

    @staticmethod
    def _parse(result: "raw.base.messages.WidgetPublicData") -> "WidgetPublicData":
        if isinstance(result, raw.types.messages.WidgetPublicDataNotModified):
            return WidgetPublicData(period=result.period)

        return WidgetPublicData(
            hash=result.hash,
            data=result.data,
            period=result.period,
        )
