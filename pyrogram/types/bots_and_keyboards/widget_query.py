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
from pyrogram import raw, types, utils

from typing import Union

from ..object import Object
from .widget_query_type import WidgetQueryType
from .widget_query_wallet import WidgetQueryWallet


class WidgetQuery(Object):
    """This object represents an incoming query from a widget in a message sent by the bot or via the bot.

    Use :meth:`~pyrogram.Client.set_bot_widget_query_answer` to answer the query.
    Each user can send at most 5 queries per 5 seconds to the bot from all its widgets.

    Parameters:
        id (``int``):
            Unique identifier for this query.

        from_user (:obj:`~pyrogram.types.User`):
            Sender.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Chat with the message containing the widget; omitted if the widget is in an inline message.

        message_id (``int``, *optional*):
            Identifier of the message containing the widget; omitted if the widget is in an inline message.

        inline_message_id (``str``, *optional*):
            Identifier of the inline message containing the widget.

        chat_instance (``str``, *optional*):
            Global identifier, uniquely corresponding to the chat to which the message with the widget was sent.

        chat_type (``str``, *optional*):
            For widgets in inline messages, type of the chat to which the message was sent.
            Can be either ``"sender"`` for a private chat with the inline query sender, ``"private"``,
            ``"group"``, ``"supergroup"``, or ``"channel"``.

        data (``str``):
            Data of the query, 1-64 bytes.

        widget_id (``int``, *optional*):
            Unique identifier of the shared widget, which sent the query; omitted if the widget isn't shared.

        shared (``bool``, *optional*):
            True, if the query was sent from a forwarded message with a shared widget
            created by the bot (Bot API ``shared_widget_query``). Such queries carry only
            ``id``, ``from_user``, ``type``, ``data`` and ``widget_id``.

        query_type (:obj:`~pyrogram.types.WidgetQueryType`):
            Type of the query.

        wallet_card (:obj:`~pyrogram.types.WidgetQueryWallet`, *optional*):
            TON wallet card of the user who sent the query, if it was sent to the bot along with the query.
    """

    def __init__(
        self,
        id: int = None,
        from_user: "types.User" = None,
        chat: "types.Chat" = None,
        message_id: int = None,
        inline_message_id: str = None,
        chat_instance: str = None,
        chat_type: str = None,
        data: str = None,
        widget_id: int = None,
        shared: bool = None,
        query_type: WidgetQueryType = None,
        wallet_card: WidgetQueryWallet = None,
        _raw: Union[
            "raw.types.UpdateBotWidgetQuery",
            "raw.types.UpdateInlineBotWidgetQuery",
            "raw.types.UpdateBotWidgetCopyQuery",
        ] = None,
    ):
        super().__init__()

        self.id = id
        self.from_user = from_user
        self.chat = chat
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.chat_instance = chat_instance
        self.chat_type = chat_type
        self.data = data
        self.widget_id = widget_id
        self.shared = shared
        self.query_type = query_type
        self.wallet_card = wallet_card
        self._raw = _raw

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        widget_query: Union[
            "raw.types.UpdateBotWidgetQuery",
            "raw.types.UpdateInlineBotWidgetQuery",
            "raw.types.UpdateBotWidgetCopyQuery",
        ],
        users: dict,
        chats: dict = None,
    ) -> "WidgetQuery":
        chat = None
        message_id = None
        inline_message_id = None
        chat_instance = None
        chat_type = None
        shared = None

        if isinstance(widget_query, raw.types.UpdateBotWidgetQuery):
            chat = types.Chat._parse(
                client,
                widget_query.peer,
                users,
                chats
            )

            if isinstance(widget_query.peer, (raw.types.PeerUser, raw.types.PeerChat, raw.types.PeerChannel)):
                message_id = widget_query.msg_id
                chat_instance = str(widget_query.chat_instance)
        elif isinstance(widget_query, raw.types.UpdateInlineBotWidgetQuery):
            inline_message_id = utils.pack_inline_message_id(
                widget_query.inline_message_id
            )
            chat_instance = str(widget_query.chat_instance)
            chat_type = widget_query.chat_type
        elif isinstance(widget_query, raw.types.UpdateBotWidgetCopyQuery):
            shared = True

        wallet_card = None

        if widget_query.wallet_card:
            wallet_card = WidgetQueryWallet._parse(widget_query.wallet_card)

        return WidgetQuery(
            id=widget_query.query_id,
            from_user=types.User._parse(client, users.get(widget_query.user_id, None)),
            chat=chat,
            message_id=message_id,
            inline_message_id=inline_message_id,
            chat_instance=chat_instance,
            chat_type=chat_type,
            data=widget_query.data.decode("utf-8", "replace"),
            widget_id=widget_query.widget_id or None,
            shared=shared,
            query_type=WidgetQueryType._parse(widget_query.query_type),
            wallet_card=wallet_card,
            _raw=widget_query
        )
