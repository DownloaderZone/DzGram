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

import pyrogram

from pyrogram import types
from ..object import Object


class MessageAutoDeleteTimerChanged(Object):
    """This object represents a service message about a change in auto-delete timer settings.

    Parameters:
        message_auto_delete_time (``int``):
            New auto-delete time for messages in the chat; in seconds.
        
        from_user (:obj:`~pyrogram.types.User`, *optional*):
            If set, the chat TTL setting was set not due to a manual change by one of participants, but automatically because one of the participants has the default TTL settings enabled.

    """

    def __init__(
        self,
        *,
        message_auto_delete_time: int = None,
        from_user: "types.User" = None
    ):
        super().__init__()

        self.message_auto_delete_time = message_auto_delete_time
        self.from_user = from_user
