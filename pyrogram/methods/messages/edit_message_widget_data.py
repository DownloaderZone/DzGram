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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types


class EditMessageWidgetData:
    async def edit_message_widget_data(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        public_data: Optional[str] = None,
        chat_data: Optional[str] = None,
    ) -> Optional["types.Message"]:
        """Edit the widget data of a message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Identifier of the chat containing the widget message.

            message_id (``int``):
                Identifier of the widget message.

            public_data (``str``, *optional*):
                New public widget data.

            chat_data (``str``, *optional*):
                New chat-specific widget data.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the edited message is returned.

        Example:
            .. code-block:: python

                await app.edit_message_widget_data(chat_id, message_id, public_data="{}")
        """
        r = await self.invoke(
            raw.functions.messages.EditMessageWidgetData(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                public_data=public_data,
                chat_data=chat_data,
            )
        )

        for i in r.updates:
            if isinstance(
                i,
                (
                    raw.types.UpdateEditMessage,
                    raw.types.UpdateEditChannelMessage,
                ),
            ):
                return await types.Message._parse(
                    self,
                    i.message,
                    {u.id: u for u in r.users},
                    {c.id: c for c in r.chats},
                    replies=self.fetch_replies,
                )

        return None
