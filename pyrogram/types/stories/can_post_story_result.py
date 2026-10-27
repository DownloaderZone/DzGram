#  DzGram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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


from ..object import Object


class CanPostStoryResult(Object):
    """This object represents result of checking whether the current user can post a story on behalf of the specific chat.

    Currently, it can be one of:

    - :obj:`~pyrogram.types.CanPostStoryResultOk`
    - :obj:`~pyrogram.types.CanPostStoryResultPremiumNeeded`
    - :obj:`~pyrogram.types.CanPostStoryResultBoostNeeded`
    - :obj:`~pyrogram.types.CanPostStoryResultActiveStoryLimitExceeded`
    - :obj:`~pyrogram.types.CanPostStoryResultWeeklyLimitExceeded`
    - :obj:`~pyrogram.types.CanPostStoryResultMonthlyLimitExceeded`
    """

    def __init__(self):
        super().__init__()
