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
from pyrogram import raw, utils


class EditInlineBotMessageWidgetData:
    async def edit_inline_bot_message_widget_data(
        self: "pyrogram.Client",
        inline_message_id: str,
        public_data: Optional[str] = None,
        chat_data: Optional[str] = None,
    ) -> bool:
        """Edit the widget data of an inline bot message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            inline_message_id (``str``):
                Identifier of the inline message.

            public_data (``str``, *optional*):
                New public widget data.

            chat_data (``str``, *optional*):
                New chat-specific widget data.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_inline_bot_message_widget_data(inline_message_id, public_data="{}")
        """
        return await self.invoke(
            raw.functions.messages.EditInlineBotMessageWidgetData(
                id=utils.unpack_inline_message_id(inline_message_id),
                public_data=public_data,
                chat_data=chat_data,
            )
        )
