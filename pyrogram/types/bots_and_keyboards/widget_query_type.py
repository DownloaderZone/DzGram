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

from pyrogram import raw

from ..object import Object
from .widget_query_wallet import WidgetQueryWallet


class WidgetQueryType(Object):
    """This object describes the type of a query from a widget.

    Currently, it can be one of:

    - :obj:`~pyrogram.types.WidgetQueryType` with ``type`` set to ``"data"``
    - :obj:`~pyrogram.types.WidgetQueryType` with ``type`` set to ``"sign_data"``
    - :obj:`~pyrogram.types.WidgetQueryType` with ``type`` set to ``"sent_transaction"``

    Parameters:
        type (``str``):
            Type of the query. Can be ``"data"``, ``"sign_data"`` or ``"sent_transaction"``.

        with_wallet (``bool``, *optional*):
            True, if the query was sent to the bot together with the TON wallet card of the user
            (see :attr:`~pyrogram.types.WidgetQuery.wallet_card`).

        wallet (:obj:`~pyrogram.types.WidgetQueryWallet`, *optional*):
            The TON wallet that signed the data or from which the transaction was sent;
            only for ``"sign_data"`` and ``"sent_transaction"`` queries.

        sign_data (``str``, *optional*):
            JSON-serialized signed data, signed by a TON wallet of the user;
            only for ``"sign_data"`` queries.

        msg_hash (``str``, *optional*):
            Value of msg_hash of the transaction sent from a TON wallet of the user;
            only for ``"sent_transaction"`` queries.
    """

    def __init__(
        self,
        type: str = None,
        with_wallet: bool = None,
        wallet: WidgetQueryWallet = None,
        sign_data: str = None,
        msg_hash: str = None,
        _raw: "raw.base.WidgetQueryType" = None,
    ):
        super().__init__()

        self.type = type
        self.with_wallet = with_wallet
        self.wallet = wallet
        self.sign_data = sign_data
        self.msg_hash = msg_hash
        self._raw = _raw

    @staticmethod
    def _parse(
        query_type: "raw.base.WidgetQueryType",
    ) -> "WidgetQueryType":
        if isinstance(query_type, raw.types.WidgetQueryTypeData):
            return WidgetQueryType(
                type="data",
                with_wallet=query_type.with_wallet or None,
                _raw=query_type,
            )

        if isinstance(query_type, raw.types.WidgetQueryTypeSignData):
            return WidgetQueryType(
                type="sign_data",
                wallet=WidgetQueryWallet._parse(query_type.wallet),
                sign_data=query_type.sign_data,
                _raw=query_type,
            )

        if isinstance(query_type, raw.types.WidgetQueryTypeSentTransaction):
            return WidgetQueryType(
                type="sent_transaction",
                wallet=WidgetQueryWallet._parse(query_type.wallet),
                msg_hash=query_type.msg_hash,
                _raw=query_type,
            )

        return WidgetQueryType(_raw=query_type)
