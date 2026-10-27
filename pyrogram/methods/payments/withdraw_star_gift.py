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
from pyrogram import raw, types


class WithdrawStarGift:
    async def withdraw_star_gift(
        self: "pyrogram.Client",
        stargift: "types.InputSavedStarGift",
        tmp_password: bytes,
        keep_on_profile: bool = False,
    ) -> bool:
        """Withdraw a star gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            stargift (:obj:`~pyrogram.types.InputSavedStarGift`):
                Identifier of the saved star gift.

            tmp_password (``bytes``):
                Temporary password obtained from :meth:`~pyrogram.Client.get_star_gift_withdrawal_url`.

            keep_on_profile (``bool``, *optional*):
                Keep the gift displayed on the profile after withdrawal.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InputSavedStarGift

                await app.withdraw_star_gift(
                    InputSavedStarGift(slug="gift-slug"),
                    tmp_password
                )
        """
        return await self.invoke(
            raw.functions.payments.WithdrawStarGift(
                keep_on_profile=keep_on_profile,
                stargift=await stargift.write(self),
                tmp_password=tmp_password,
            )
        )
