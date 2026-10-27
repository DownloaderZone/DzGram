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

from typing import List

from pyrogram import raw, types
from ..object import Object


class AgentProviders(Object):
    """Available AI agent providers.

    Parameters:
        hash (``int``):
            Hash of the list.

        providers (List of :obj:`~pyrogram.types.AgentProvider`):
            The providers.
    """

    def __init__(
        self,
        *,
        hash: int = 0,
        providers: List["types.AgentProvider"] = None,
    ):
        super().__init__()

        self.hash = hash
        self.providers = providers or []

    @staticmethod
    def _parse(result: "raw.base.agent.Providers") -> "AgentProviders":
        if isinstance(result, raw.types.agent.ProvidersNotModified):
            return AgentProviders()

        return AgentProviders(
            hash=result.hash,
            providers=types.List(
                [types.AgentProvider._parse(provider) for provider in result.providers]
            ),
        )
