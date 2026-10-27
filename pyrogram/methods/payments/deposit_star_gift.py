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

from typing import Union

import pyrogram
from pyrogram import raw, types


class DepositStarGift:
    async def deposit_star_gift(
        self: "pyrogram.Client",
        slug: str,
        chat_id: Union[int, str],
        hide_sender: bool = False,
    ) -> "types.StarGiftDepositPayload":
        """Get the payload needed to deposit a star gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            slug (``str``):
                Unique slug of the gift.

            chat_id (``int`` | ``str``):
                Identifier of the chat that will receive the deposit.

            hide_sender (``bool``, *optional*):
                Hide the sender of the gift.

        Returns:
            :obj:`~pyrogram.types.StarGiftDepositPayload`: The deposit payload.

        Example:
            .. code-block:: python

                payload = await app.deposit_star_gift("gift-slug", chat_id)
                print(payload.nft_address)
        """
        result = await self.invoke(
            raw.functions.payments.DepositStarGift(
                hide_sender=hide_sender,
                peer=await self.resolve_peer(chat_id),
                slug=slug,
            )
        )

        return types.StarGiftDepositPayload._parse(result)
