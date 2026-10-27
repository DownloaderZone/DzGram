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


class GetAgentSettings:
    async def get_agent_settings(
        self: "pyrogram.Client",
    ) -> "types.AgentSettings":
        """Get the AI agent settings.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.types.AgentSettings`: The settings.

        Example:
            .. code-block:: python

                settings = await app.get_agent_settings()
        """
        return types.AgentSettings._parse(
            await self.invoke(
                raw.functions.agent.GetSettings()
            )
        )
