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

import logging
from typing import Union, Optional

import pyrogram
from pyrogram import raw, types

log = logging.getLogger(__name__)


class EditEphemeralMessageReplyMarkup:
    async def edit_ephemeral_message_reply_markup(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,
    ) -> "types.Message":
        """Edit only the reply markup of an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message to edit.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited ephemeral message is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                # Edit ephemeral message reply markup
                await app.edit_ephemeral_message_reply_markup(
                    chat_id, message_id,
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("New button", callback_data="new_data")]]))
        """
        r = await self.invoke(
            raw.functions.ephemeral.EditMessageReplyMarkup(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
            )
        )

        for u in getattr(r, "updates", []):
            if isinstance(u, raw.types.UpdateNewEphemeralMessage):
                return await types.Message._parse(
                    client=self,
                    message=u.message,
                    users={i.id: i for i in getattr(r, "users", [])},
                    chats={i.id: i for i in getattr(r, "chats", [])},
                )

        return None
