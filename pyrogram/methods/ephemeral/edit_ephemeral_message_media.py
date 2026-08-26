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
from pyrogram import raw, types, utils

log = logging.getLogger(__name__)


class EditEphemeralMessageMedia:
    async def edit_ephemeral_message_media(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        media: "types.InputMedia",
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,
    ) -> "types.Message":
        """Edit the media of an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message to edit.

            media (:obj:`~pyrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited ephemeral message is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto

                # Edit an ephemeral message media
                await app.edit_ephemeral_message_media(chat_id, message_id,
                    InputMediaPhoto("new_photo.jpg"))
        """
        caption = media.caption
        parse_mode = media.parse_mode
        caption_entities = media.caption_entities

        message, entities = None, None

        if caption is not None:
            message, entities = (await utils.parse_text_entities(self, caption, parse_mode, caption_entities)).values()

        if media is not None and not isinstance(
            media,
            (
                types.InputMediaPhoto,
                types.InputMediaVideo,
                types.InputMediaAudio,
                types.InputMediaAnimation,
                types.InputMediaDocument,
            ),
        ):
            raise ValueError(f"Unsupported media type: {type(media)}")

        raw_media, _show_caption_above_media = await media.write(
            client=self,
            chat_id=chat_id,
        )

        r = await self.invoke(
            raw.functions.ephemeral.EditMessageMedia(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                media=raw_media,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=message,
                entities=entities,
                invert_media=_show_caption_above_media,
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
