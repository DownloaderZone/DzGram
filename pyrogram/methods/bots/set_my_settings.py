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
from pyrogram import raw

from ...types import BotSettings


class SetMySettings:
    async def set_my_settings(
        self: "pyrogram.Client",
        inline_mode: bool = None,
        privacy_mode: bool = None,
        can_join_groups: bool = None,
        forum_topic_mode: bool = None,
        callback_query_inline: bool = None,
        has_topic_sidebar: bool = None,
    ) -> bool:
        """Use this method to change the settings of the current bot (Bot API 10.5).

        Only the bot's owner can call this method. Flags omitted (or passed as
        ``False``) are left unchanged on the wire; passing ``True`` enables the
        setting.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            inline_mode (``bool``, *optional*):
                True, to enable inline queries for the bot.

            privacy_mode (``bool``, *optional*):
                True, to enable the bot's privacy mode: the bot only receives
                messages that start with a command, replies to its own messages,
                service messages and messages from channels where it is a member.

            can_join_groups (``bool``, *optional*):
                True, to allow the bot to be added to groups.

            forum_topic_mode (``bool``, *optional*):
                True, to publish new topics created by the bot in a separate
                sidebar.

            callback_query_inline (``bool``, *optional*):
                True, to allow inline queries triggered by callback query
                buttons (press-in-app queries).

            has_topic_sidebar (``bool``, *optional*):
                True, to show the topic sidebar for the bot's forum topics.

        Raises:
            :obj:`~pyrogram.errors.RPCError`: In case of a Telegram RPC error.

        Returns:
            ``bool``: True, on success.

        Example:
            .. code-block:: python

                await app.set_my_settings(inline_mode=True)
        """

        return bool(
            await self.invoke(
                raw.functions.bots.SetMySettings(
                    settings=BotSettings(
                        inline_mode=inline_mode,
                        privacy_mode=privacy_mode,
                        can_join_groups=can_join_groups,
                        forum_topic_mode=forum_topic_mode,
                        callback_query_inline=callback_query_inline,
                        has_topic_sidebar=has_topic_sidebar,
                    ).write()
                )
            )
        )
