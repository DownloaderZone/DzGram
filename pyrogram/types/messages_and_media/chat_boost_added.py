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

from pyrogram import raw
from ..object import Object


class ChatBoostAdded(Object):
    """This object represents a service message about a user boosting a chat.

    Parameters:
        boost_count (``int``):
            Number of boosts added by the user

    """

    def __init__(
        self,
        *,
        boost_count: int,
    ):
        super().__init__()

        self.boost_count = boost_count

    @staticmethod
    def _parse(action: "raw.types.MessageActionBoostApply"):
        return ChatBoostAdded(
            boost_count=action.boosts
        )
