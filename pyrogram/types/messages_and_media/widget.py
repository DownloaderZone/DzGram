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

import zlib

from pyrogram import raw

from ..object import Object


class Widget(Object):
    """This object describes an HTML widget (Bot API 10.4).

    Parameters:
        id (``int``, *optional*):
            Unique identifier of the shared widget, which can be used to send the widget again
            using :meth:`~pyrogram.Client.send_shared_widget`; omitted if the widget isn't shared.

        width (``int``, *optional*):
            Width of the widget in logical pixels; omitted if the widget must occupy
            the whole width of the message bubble.

        height (``int``, *optional*):
            Height of the widget in logical pixels; omitted if the height of the widget isn't fixed.

        html (``str``):
            HTML code of the widget.

        public_data (``str``, *optional*):
            Public data of the widget, which is available wherever the widget is shown.
            All messages with a shared widget have the same public data.

        chat_data (``str``, *optional*):
            Data of the widget, which is specific to the message.
    """

    def __init__(
        self,
        id: int = None,
        width: int = None,
        height: int = None,
        html: str = None,
        public_data: str = None,
        chat_data: str = None,
        _raw: "raw.types.MessageMediaWidget" = None,
    ):
        super().__init__()

        self.id = id
        self.width = width
        self.height = height
        self.html = html
        self.public_data = public_data
        self.chat_data = chat_data
        self._raw = _raw

    @staticmethod
    def _parse(
        message_media_widget: "raw.types.MessageMediaWidget"
    ) -> "Widget":
        try:
            html = zlib.decompress(message_media_widget.payload).decode("utf-8", "replace")
        except zlib.error:
            html = message_media_widget.payload.decode("utf-8", "replace")

        return Widget(
            id=message_media_widget.widget_id or None,
            width=message_media_widget.width,
            height=message_media_widget.height,
            html=html,
            public_data=message_media_widget.public_data,
            chat_data=message_media_widget.chat_data,
            _raw=message_media_widget
        )
