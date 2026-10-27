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


class RtmpUrl(Object):
    """Represents an RTMP URL and stream key to be used in streaming software.

    Parameters:
        url (``str``):
            The URL.

        stream_key (``str``):
            Stream key.

    """

    def __init__(self, *, url: str, stream_key: str):
        super().__init__(None)

        self.url = url
        self.stream_key = stream_key

    @staticmethod
    def _parse(rtmp_url: "raw.types.GroupCallStreamRtmpUrl") -> "RtmpUrl":
        return RtmpUrl(
            url=rtmp_url.url,
            stream_key=rtmp_url.key
        )
