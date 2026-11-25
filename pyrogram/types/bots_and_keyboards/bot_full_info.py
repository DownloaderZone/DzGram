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

from typing import List

from pyrogram import raw

from ..object import Object
from .bot_settings import BotSettings


class BotFullInfo(Object):
    """This object contains full information about a bot (Bot API 10.5).

    Parameters:
        active_usernames (List of ``str``, *optional*):
            Usernames of the bot that are active.

        inline_query_placeholder (``str``, *optional*):
            Placeholder shown in the inline query input field.

        needs_inline_query_location (``bool``, *optional*):
            True, if the bot requires the user location in inline queries.

        has_topic_sidebar (``bool``, *optional*):
            True, if the topic sidebar is shown for the bot's forum topics.

        settings (:obj:`~pyrogram.types.BotSettings`, *optional*):
            Settings of the bot.
    """

    def __init__(
        self,
        *,
        active_usernames: List[str] = None,
        inline_query_placeholder: str = None,
        needs_inline_query_location: bool = None,
        has_topic_sidebar: bool = None,
        settings: BotSettings = None,
        _raw: "raw.base.bots.BotFullInfo" = None,
    ):
        super().__init__()

        self.active_usernames = active_usernames
        self.inline_query_placeholder = inline_query_placeholder
        self.needs_inline_query_location = needs_inline_query_location
        self.has_topic_sidebar = has_topic_sidebar
        self.settings = settings
        self._raw = _raw

    @staticmethod
    def _parse(full_info: "raw.base.bots.BotFullInfo") -> "BotFullInfo":
        return BotFullInfo(
            active_usernames=full_info.active_usernames or None,
            inline_query_placeholder=full_info.inline_query_placeholder or None,
            needs_inline_query_location=full_info.needs_inline_query_location or None,
            has_topic_sidebar=full_info.has_topic_sidebar or None,
            settings=BotSettings._parse(full_info.settings) if full_info.settings else None,
            _raw=full_info,
        )
