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


class AgentProviderKey(Object):
    """A saved AI agent provider key.

    Parameters:
        provider (``str``):
            Identifier of the provider.

        key_last4 (``str``):
            Last four characters of the key.

        date_connected (``int``):
            Date when the key was connected.
    """

    def __init__(
        self,
        *,
        provider: str,
        key_last4: str,
        date_connected: int,
    ):
        super().__init__()

        self.provider = provider
        self.key_last4 = key_last4
        self.date_connected = date_connected

    @staticmethod
    def _parse(key: "raw.types.agent.ProviderKey") -> "AgentProviderKey":
        return AgentProviderKey(
            provider=key.provider,
            key_last4=key.key_last4,
            date_connected=key.date_connected,
        )
