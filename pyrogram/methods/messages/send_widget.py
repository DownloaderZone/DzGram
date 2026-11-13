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

from datetime import datetime
from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils


class SendWidget:
    async def send_widget(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        html: str,
        width: int = None,
        height: int = None,
        public_data: str = None,
        chat_data: str = None,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: list["types.MessageEntity"] = None,
        show_caption_above_media: bool = None,
        allow_queries: bool = None,
        is_shared: bool = None,
        disable_notification: bool = None,
        protect_content: bool = None,
        allow_paid_broadcast: bool = None,
        message_effect_id: int = None,
        reply_parameters: "types.ReplyParameters" = None,
        send_as: Union[int, str] = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None,
        schedule_date: datetime = None
    ) -> "types.Message":
        """Send a message with an HTML widget (Bot API 10.4).

        Currently, in the production environment, widgets can be sent only to private chats,
        and sent widgets automatically have protected content and therefore can't be forwarded.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat or username of the target supergroup
                (in the format @channelusername).

            html (``str``):
                HTML code of the widget, 1-32768 bytes. The code must not exceed 4096 bytes
                when compressed by zlib with the maximum compression level.

            width (``int``, *optional*):
                Width of the widget in logical pixels; omit if the widget must occupy
                the whole width of the message bubble.

            height (``int``, *optional*):
                Height of the widget in logical pixels; omit if the height of the widget isn't fixed.

            public_data (``str``, *optional*):
                Public data of the widget, 0-1024 bytes, which will be available wherever
                the widget is shown. If the widget is shared, then all messages with it
                will have the same public data.

            chat_data (``str``, *optional*):
                Data of the widget, which is specific to the message, 0-1024 bytes.

            caption (``str``, *optional*):
                Widget caption, 0-1024 characters after entities parsing.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified
                instead of *parse_mode*.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the widget.

            allow_queries (``bool``, *optional*):
                Pass True to allow the widget to send queries to the bot.

            is_shared (``bool``, *optional*):
                Pass True to create a shared widget, which can be sent again using
                :meth:`~pyrogram.Client.send_shared_widget`.

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Pass True if the content of the message must be protected from forwarding
                and saving; for bots only.

            allow_paid_broadcast (``bool``, *optional*):
                Pass True to allow the message to ignore regular broadcast limits for a small fee; for bots only.

            message_effect_id (``int`` ``64-bit``, *optional*):
                Unique identifier of the message effect to be added to the message; for private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Description of the message to reply to.

            send_as (``int`` | ``str``):
                Unique identifier (int) or username (str) of the chat or channel to send the message as.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            schedule_date (:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent. Pass a :obj:`~datetime.datetime` object.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Example:
            .. code-block:: python

                await app.send_widget(
                    chat_id=chat_id,
                    html="<h1>Hello</h1><script>...</script>",
                    allow_queries=True
                )
        """
        reply_to = await utils._get_reply_message_parameters(
            self,
            reply_parameters=reply_parameters
        )

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaWidget(
                    allow_queries=allow_queries,
                    shared_widget=is_shared,
                    width=width,
                    height=height,
                    html=html,
                    public_data=public_data,
                    chat_data=chat_data,
                ),
                random_id=self.rnd_id(),
                silent=disable_notification or None,
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                reply_to=reply_to,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                invert_media=show_caption_above_media,
                effect=message_effect_id,
                send_as=await self.resolve_peer(send_as) if send_as else None,
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
            )
        )

        for i in r.updates:
            if isinstance(
                i,
                (
                    raw.types.UpdateNewMessage,
                    raw.types.UpdateNewChannelMessage,
                    raw.types.UpdateNewScheduledMessage
                )
            ):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                    replies=self.fetch_replies
                )
