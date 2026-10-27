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

from typing import Optional

import pyrogram
from pyrogram import raw, types
from ..object import Object
from ..update import Update


class MessageGenerationStopped(Object, Update):
    """This object describes an update about a user stopping message generation.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            Chat in which the message is generated.

        message_thread_id (``int``, *optional*):
            Unique identifier of the message thread in which the message is generated.

        draft_id (``int``):
            Unique identifier of the message draft which was stopped.
    """

    def __init__(
        self,
        *,
        chat: "types.Chat",
        draft_id: int,
        message_thread_id: Optional[int] = None
    ):
        super().__init__()

        self.chat = chat
        self.message_thread_id = message_thread_id
        self.draft_id = draft_id

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        update: "raw.types.UpdateUserTyping",
        users: dict,
        chats: dict
    ) -> "MessageGenerationStopped":
        action: "raw.types.SendMessageStopDraftAction" = update.action
        raw_chat = (
            users.get(getattr(update, "user_id", None))
            or chats.get(getattr(update, "chat_id", None))
            or chats.get(getattr(update, "channel_id", None))
        )

        return MessageGenerationStopped(
            chat=types.Chat._parse_chat(client, raw_chat),
            message_thread_id=getattr(update, "top_msg_id", None),
            draft_id=action.random_id,
        )
