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

from pyrogram import raw

from ..object import Object


class BotSettings(Object):
    """This object describes the settings of a bot (Bot API 10.5).

    Parameters:
        inline_mode (``bool``):
            True, if the bot supports inline queries.

        privacy_mode (``bool``):
            True, if the bot's privacy mode is enabled: the bot only receives
            messages that start with a command, replies to its own messages,
            service messages and messages from channels where it is a member.

        can_join_groups (``bool``):
            True, if the bot can be added to groups.

        forum_topic_mode (``bool``):
            True, if new topics created by the bot are published in a separate
            sidebar (requires the topic sidebar to be available for the bot).

        callback_query_inline (``bool``):
            True, if inline queries triggered by callback query buttons
            (press-in-app queries) are allowed for the bot.

        has_topic_sidebar (``bool``):
            True, if the topic sidebar is shown for the bot's forum topics.
    """

    def __init__(
        self,
        *,
        inline_mode: bool = None,
        privacy_mode: bool = None,
        can_join_groups: bool = None,
        forum_topic_mode: bool = None,
        callback_query_inline: bool = None,
        has_topic_sidebar: bool = None,
        _raw: "raw.base.bots.BotSettings" = None,
    ):
        super().__init__()

        self.inline_mode = inline_mode
        self.privacy_mode = privacy_mode
        self.can_join_groups = can_join_groups
        self.forum_topic_mode = forum_topic_mode
        self.callback_query_inline = callback_query_inline
        self.has_topic_sidebar = has_topic_sidebar
        self._raw = _raw

    @staticmethod
    def _parse(settings: "raw.base.bots.BotSettings") -> "BotSettings":
        return BotSettings(
            inline_mode=settings.inline_mode or None,
            privacy_mode=settings.privacy_mode or None,
            can_join_groups=settings.can_join_groups or None,
            forum_topic_mode=settings.forum_topic_mode or None,
            callback_query_inline=settings.callback_query_inline or None,
            has_topic_sidebar=settings.has_topic_sidebar or None,
            _raw=settings,
        )

    def write(self) -> "raw.base.bots.BotSettings":
        return raw.types.bots.BotSettings(
            inline_mode=self.inline_mode or None,
            privacy_mode=self.privacy_mode or None,
            can_join_groups=self.can_join_groups or None,
            forum_topic_mode=self.forum_topic_mode or None,
            callback_query_inline=self.callback_query_inline or None,
            has_topic_sidebar=self.has_topic_sidebar or None,
        )
