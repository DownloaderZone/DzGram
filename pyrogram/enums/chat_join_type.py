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


class ChatJoinType(AutoName):
    """How the service message :obj:`~pyrogram.enums.MessageServiceType.NEW_CHAT_MEMBERS` was used for the member to join the chat."""

    BY_ADD = auto()
    "New chat members were added. ``from_user`` will contain the actor. ``new_chat_members`` will contain the user identifiers of the new members."

    BY_LINK = auto()
    "A new member joined the chat via an invite link"

    BY_REQUEST = auto()
    "A new member was accepted to the chat by an administrator"
