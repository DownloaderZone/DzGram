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


class ForwardMessage:
    async def forward_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
    ) -> Optional["types.Message"]:
        """Forward a single message.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Message identifier in the target chat.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the forwarded message is returned.

        Example:
            .. code-block:: python

                await app.forward_message("me", 123)
        """
        r = await self.invoke(
            raw.functions.messages.ForwardMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                random_id=self.rnd_id(),
            )
        )

        for i in r.updates:
            if isinstance(
                i,
                (
                    raw.types.UpdateNewMessage,
                    raw.types.UpdateNewChannelMessage,
                    raw.types.UpdateNewScheduledMessage,
                ),
            ):
                return await types.Message._parse(
                    self,
                    i.message,
                    {u.id: u for u in r.users},
                    {c.id: c for c in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                    replies=self.fetch_replies,
                )

        return None
