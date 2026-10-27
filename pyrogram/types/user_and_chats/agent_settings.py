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

from typing import List, Optional

from pyrogram import raw, types
from ..object import Object


class AgentSettings(Object):
    """AI agent settings.

    Parameters:
        keys (List of :obj:`~pyrogram.types.AgentProviderKey`):
            Saved provider keys.

        active_provider (``str``, *optional*):
            Identifier of the active provider.
    """

    def __init__(
        self,
        *,
        keys: List["types.AgentProviderKey"],
        active_provider: Optional[str] = None,
    ):
        super().__init__()

        self.keys = keys
        self.active_provider = active_provider

    @staticmethod
    def _parse(settings: "raw.types.agent.Settings") -> "AgentSettings":
        return AgentSettings(
            keys=types.List(
                [types.AgentProviderKey._parse(key) for key in settings.keys]
            ),
            active_provider=getattr(settings, "active_provider", None),
        )
