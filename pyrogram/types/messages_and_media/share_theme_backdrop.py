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
from pyrogram import raw
from ..object import Object


class ShareThemeBackdrop(Object):
    """A backdrop that can be used for share themes.

    Parameters:
        backdrop_id (``int``):
            Unique identifier of the backdrop.

        name (``str``):
            Name of the backdrop.

        center_color (``int``):
            Center color.

        edge_color (``int``):
            Edge color.

        pattern_color (``int``):
            Pattern color.

        text_color (``int``):
            Text color.
    """

    def __init__(
        self,
        *,
        backdrop_id: int,
        name: str,
        center_color: int,
        edge_color: int,
        pattern_color: int,
        text_color: int,
    ):
        super().__init__()

        self.backdrop_id = backdrop_id
        self.name = name
        self.center_color = center_color
        self.edge_color = edge_color
        self.pattern_color = pattern_color
        self.text_color = text_color

    @staticmethod
    def _parse(backdrop: "raw.types.ShareThemeBackdropOption") -> "ShareThemeBackdrop":
        return ShareThemeBackdrop(
            backdrop_id=backdrop.backdrop_id,
            name=backdrop.name,
            center_color=backdrop.center_color,
            edge_color=backdrop.edge_color,
            pattern_color=backdrop.pattern_color,
            text_color=backdrop.text_color,
        )
