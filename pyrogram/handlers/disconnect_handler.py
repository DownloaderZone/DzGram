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

from typing import Any, Callable

import pyrogram
from .handler import Handler

CallbackFunc: Callable = Callable[["pyrogram.Client"], Any]


class DisconnectHandler(Handler):
    """The Disconnect handler class. Used to handle disconnections. It is intended to be used with
    :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_disconnect` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a disconnection occurs. It takes *(client)*
            as positional argument (look at the section below for a detailed description).

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself. Useful, for example, when you want to change the proxy before a new connection
            is established.

    """

    def __init__(self, callback: CallbackFunc):
        super().__init__(callback)
