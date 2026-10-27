#  DzGram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
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

from enum import auto

from .auto_name import AutoName


class ButtonStyle(AutoName):
    """Button style type enumeration used in :obj:`~pyrogram.types.KeyboardButton` and :obj:`~pyrogram.types.InlineKeyboardButton` to describe the style of a button."""

    DEFAULT = auto()
    "The button has default style"

    PRIMARY = auto()
    "The button has dark blue color"

    DANGER = auto()
    "The button has red color"

    SUCCESS = auto()
    "The button has green color"
