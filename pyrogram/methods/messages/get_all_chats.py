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

import pyrogram
from pyrogram import raw, types


class GetAllChats:
    async def get_all_chats(
        self: "pyrogram.Client",
        except_ids: Optional[List[int]] = None,
    ) -> List["types.Chat"]:
        """Get all chats the current user is a member of.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            except_ids (List of ``int``, *optional*):
                Identifiers of chats to exclude from the result.

        Returns:
            List of :obj:`~pyrogram.types.Chat`: The chats.

        Example:
            .. code-block:: python

                chats = await app.get_all_chats()
        """
        r = await self.invoke(
            raw.functions.messages.GetAllChats(
                except_ids=except_ids or []
            )
        )

        return [types.Chat._parse_chat(self, chat) for chat in r.chats]
