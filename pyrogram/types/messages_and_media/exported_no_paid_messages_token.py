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

from datetime import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, utils
from ..object import Object


class ExportedNoPaidMessagesToken(Object):
    """A token that allows a user to send paid messages to the current user without paying.

    Parameters:
        token (``str``):
            The token.

        url (``str``):
            URL that can be used to import the token.

        expires (:py:obj:`~datetime.datetime`, *optional*):
            Expiration date of the token.
    """

    def __init__(
        self,
        *,
        token: str,
        url: str,
        expires: Optional[datetime] = None,
    ):
        super().__init__()

        self.token = token
        self.url = url
        self.expires = expires

    @staticmethod
    def _parse(token: "raw.types.ExportedNoPaidMessagesToken") -> "ExportedNoPaidMessagesToken":
        return ExportedNoPaidMessagesToken(
            token=token.token,
            url=token.url,
            expires=utils.timestamp_to_datetime(token.expires),
        )
