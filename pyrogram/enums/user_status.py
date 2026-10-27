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

from enum import auto

from .auto_name import AutoName


class UserStatus(AutoName):
    """User status enumeration used in :obj:`~pyrogram.types.User`."""

    ONLINE = auto()
    """User is online"""

    OFFLINE = auto()
    """User is offline"""

    RECENTLY = auto()
    """User was seen recently"""

    LAST_WEEK = auto()
    """User was seen last week"""

    LAST_MONTH = auto()
    """User was seen last month"""

    HIDDEN = auto()
    """User status is hidden"""

    LONG_AGO = auto()
    """User was seen long ago"""
