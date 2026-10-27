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
from pyrogram import raw
from pyrogram import types


class JoinChat:
    async def join_chat(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        for_news: bool = None,
    ) -> "types.Chat":
        """Join a group chat or channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, a username of the target
                channel/supergroup (in the format @username) or a chat id of a linked chat (channel or supergroup).

            for_news (``bool``, *optional*):
                Pass True to join a channel as a news channel.

        Returns:
            :obj:`~pyrogram.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                # Join chat via invite link
                await app.join_chat("https://t.me/+AbCdEf0123456789")

                # Join chat via username
                await app.join_chat("pyrogram")

                # Join chat via Telegram Public Link
                await app.join_chat("https://t.me/pyrogram")

                # Join a linked chat
                await app.join_chat((await app.get_chat("pyrogram")).linked_chat.id)
        """
        match = self.INVITE_LINK_RE.match(str(chat_id))

        if match:
            result = await self.invoke(
                raw.functions.messages.ImportChatInvite(
                    hash=match.group(1)
                )
            )

            return await self._parse_join_result(result)
        else:
            match2 = self.TME_PUBLIC_LINK_RE.match(str(chat_id))
            if match2:
                chat_id = match2.group(1) or match2.group(2) or chat_id
            result = await self.invoke(
                raw.functions.channels.JoinChannel(
                    channel=await self.resolve_peer(chat_id),
                    for_news=for_news or None,
                )
            )

            return await self._parse_join_result(result, chat_id)

    async def _parse_join_result(
        self: "pyrogram.Client",
        result: "raw.base.messages.ChatInviteJoinResult",
        chat_id: Optional[Union[int, str]] = None,
    ) -> "types.Chat":
        if isinstance(result, raw.types.messages.ChatInviteJoinResultOk):
            chats = getattr(result.updates, "chats", None) or []

            if chats:
                chat = chats[0]

                if isinstance(chat, raw.types.Chat):
                    return types.Chat._parse_chat_chat(self, chat)
                elif isinstance(chat, raw.types.Channel):
                    return types.Chat._parse_channel_chat(self, chat)

            if chat_id is not None:
                return await self.get_chat(chat_id)

            raise ValueError("Telegram did not return the joined chat")
        elif isinstance(result, raw.types.messages.ChatInviteJoinResultWebView):
            users = {user.id: user for user in result.users}
            bot = users.get(result.bot_id)
            bot_name = f"@{bot.username}" if bot is not None and bot.username else "a guard bot"

            raise ValueError(
                f"Joining this chat requires approval from {bot_name} through a Web App"
            )

        raise ValueError(f"Unexpected join result: {type(result).__name__}")
