#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import pyrogram
from pyrogram import raw
from ..object import Object


class StarGiftDepositPayload(Object):
    """A payload used to deposit a star gift.

    Parameters:
        nft_address (``str``):
            Address of the NFT.

        payload (``bytes``):
            Deposit payload.

        amount (``int``):
            Deposit amount.
    """

    def __init__(self, *, nft_address: str, payload: bytes, amount: int):
        super().__init__()

        self.nft_address = nft_address
        self.payload = payload
        self.amount = amount

    @staticmethod
    def _parse(payload: "raw.types.payments.StarGiftDepositPayload") -> "StarGiftDepositPayload":
        return StarGiftDepositPayload(
            nft_address=payload.nft_address,
            payload=payload.payload,
            amount=payload.amount,
        )
