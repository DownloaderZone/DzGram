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
from pyrogram import raw, types


class ConnectAgent:
    async def connect_agent(
        self: "pyrogram.Client",
        provider: str,
        key: str,
    ) -> "types.AgentSettings":
        """Connect an AI agent provider.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                Identifier of the provider.

            key (``str``):
                Provider API key.

        Returns:
            :obj:`~pyrogram.types.AgentSettings`: The updated settings.

        Example:
            .. code-block:: python

                settings = await app.connect_agent("provider", "key")
        """
        return types.AgentSettings._parse(
            await self.invoke(
                raw.functions.agent.Connect(
                    provider=provider,
                    key=key,
                )
            )
        )
