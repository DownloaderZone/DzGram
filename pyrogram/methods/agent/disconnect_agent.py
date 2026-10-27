#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import pyrogram
from pyrogram import raw, types


class DisconnectAgent:
    async def disconnect_agent(
        self: "pyrogram.Client",
        provider: str,
    ) -> "types.AgentSettings":
        """Disconnect an AI agent provider.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                Identifier of the provider.

        Returns:
            :obj:`~pyrogram.types.AgentSettings`: The updated settings.

        Example:
            .. code-block:: python

                settings = await app.disconnect_agent("provider")
        """
        return types.AgentSettings._parse(
            await self.invoke(
                raw.functions.agent.Disconnect(
                    provider=provider
                )
            )
        )
