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

import pyrogram
from pyrogram import raw


class EditWidgetData:
    async def edit_widget_data(
        self: "pyrogram.Client",
        widget_id: int,
        public_data: str,
        cache_time: Optional[int] = None,
    ) -> bool:
        """Edit the public data of a widget.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            widget_id (``int``):
                Identifier of the widget.

            public_data (``str``):
                New public data.

            cache_time (``int``, *optional*):
                Cache time in seconds.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_widget_data(widget_id, "{}")
        """
        return await self.invoke(
            raw.functions.messages.EditWidgetData(
                widget_id=widget_id,
                public_data=public_data,
                cache_time=cache_time,
            )
        )
