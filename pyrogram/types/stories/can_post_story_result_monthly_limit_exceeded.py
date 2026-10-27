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


from .can_post_story_result import CanPostStoryResult


class CanPostStoryResultMonthlyLimitExceeded(CanPostStoryResult):
    """The monthly limit for the number of posted stories exceeded. The user needs to buy Telegram Premium or wait specified time.

    Parameters:
        retry_after (``int``):
            Time left before the user can post the next story.

    """

    def __init__(
        self,
        retry_after: int,
    ):
        super().__init__()

        self.retry_after = retry_after
