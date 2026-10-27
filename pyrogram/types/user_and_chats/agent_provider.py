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

from pyrogram import raw
from ..object import Object


class AgentProvider(Object):
    """An AI agent provider.

    Parameters:
        id (``str``):
            Identifier of the provider.

        title (``str``):
            Title of the provider.

        vendor (``str``):
            Vendor of the provider.

        key_url (``str``):
            URL where an API key can be obtained.

        icon_emoji_id (``int``, *optional*):
            Identifier of the custom emoji used as icon.

        models_searchable (``bool``, *optional*):
            True, if the provider models can be searched.
    """

    def __init__(
        self,
        *,
        id: str,
        title: str,
        vendor: str,
        key_url: str,
        icon_emoji_id: Optional[int] = None,
        models_searchable: Optional[bool] = None,
    ):
        super().__init__()

        self.id = id
        self.title = title
        self.vendor = vendor
        self.key_url = key_url
        self.icon_emoji_id = icon_emoji_id
        self.models_searchable = models_searchable

    @staticmethod
    def _parse(provider: "raw.types.AgentProvider") -> "AgentProvider":
        return AgentProvider(
            id=provider.id,
            title=provider.title,
            vendor=provider.vendor,
            key_url=provider.key_url,
            icon_emoji_id=getattr(provider, "icon_emoji_id", None),
            models_searchable=getattr(provider, "models_searchable", None),
        )
