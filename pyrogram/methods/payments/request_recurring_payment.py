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
from pyrogram import raw, types, utils


class RequestRecurringPayment:
    async def request_recurring_payment(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        recurring_init_charge: str,
        invoice_media: Union["types.InputMediaPhoto", "types.InputMediaVideo"],
    ) -> bool:
        """Request a recurring payment from a user.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Identifier of the user.

            recurring_init_charge (``str``):
                The initial recurring charge.

            invoice_media (:obj:`~pyrogram.types.InputMediaPhoto` | :obj:`~pyrogram.types.InputMediaVideo`):
                Media to attach to the invoice.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.request_recurring_payment(
                    user_id, "init", types.InputMediaPhoto("photo.jpg"))
        """
        media = await invoice_media.write(self, chat_id=user_id)

        if isinstance(media, tuple):
            media = media[0]

        await self.invoke(
            raw.functions.payments.RequestRecurringPayment(
                user_id=await utils.get_input_user(self, user_id),
                recurring_init_charge=recurring_init_charge,
                invoice_media=media,
            )
        )

        return True
