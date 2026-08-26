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
from typing import Union, List, Optional

import pyrogram
from pyrogram import raw, types, utils, enums

log = logging.getLogger(__name__)


class EditEphemeralMessageCaption:
    async def edit_ephemeral_message_caption(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,
        show_caption_above_media: Optional[bool] = None,
        rich_message: Optional[str] = None,
    ) -> "types.Message":
        """Edit the caption of an ephemeral media message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message to edit.

            caption (``str``, *optional*):
                New caption of the media message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in caption, which can be specified
                instead of *parse_mode*.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.
                Supported only for animation, photo and video messages.

            rich_message (``str``, *optional*):
                Rich text (Markdown or HTML) to render a styled caption.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited ephemeral message is returned.

        Example:
            .. code-block:: python

                # Edit an ephemeral message caption
                await app.edit_ephemeral_message_caption(chat_id, message_id, "new caption")
        """
        if rich_message is not None:
            if parse_mode == enums.ParseMode.HTML:
                rich_msg = raw.types.InputRichMessageHTML(html=rich_message)
            else:
                rich_msg = raw.types.InputRichMessageMarkdown(markdown=rich_message)
            message = ""
            entities = None
            rich_message_raw = rich_msg
        else:
            plain_text, parsed_entities = (await utils.parse_text_entities(self, caption, parse_mode, entities)).values()
            message = plain_text
            entities = parsed_entities
            rich_message_raw = None

        r = await self.invoke(
            raw.functions.ephemeral.EditMessageCaption(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                message=message,
                entities=entities or None,
                rich_message=rich_message_raw,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                invert_media=show_caption_above_media,
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
