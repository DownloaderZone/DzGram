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

import base64
from typing import Union

from pyrogram import raw

from ..object import Object


class WidgetQueryWallet(Object):
    """This object describes a TON wallet of a user, which is used in a query from a widget.

    Parameters:
        address (``str``):
            Address of the wallet.

        balance (``int``):
            Balance of the wallet, in the smallest units of the cryptocurrency.

        public_key (``str``, *optional*):
            Hex-encoded public key of the wallet; omitted if unknown.

        state_init (``str``, *optional*):
            Base64-encoded serialized StateInit of the wallet contract; omitted if and only if
            ``public_key`` is omitted.
    """

    def __init__(
        self,
        address: str = None,
        balance: int = None,
        public_key: str = None,
        state_init: str = None,
        _raw: "raw.types.UserWallet" = None,
    ):
        super().__init__()

        self.address = address
        self.balance = balance
        self.public_key = public_key
        self.state_init = state_init
        self._raw = _raw

    @staticmethod
    def _parse(
        wallet: Union["raw.types.UserWallet", "raw.types.wallet.Card"]
    ) -> "WidgetQueryWallet":
        if isinstance(wallet, raw.types.wallet.Card):
            return WidgetQueryWallet(
                address=wallet.address,
                balance=wallet.balance,
                _raw=wallet,
            )

        return WidgetQueryWallet(
            address=wallet.address,
            balance=wallet.balance,
            public_key=wallet.public_key.hex() if wallet.public_key else None,
            state_init=base64.b64encode(wallet.state_init).decode() if wallet.state_init else None,
            _raw=wallet,
        )
