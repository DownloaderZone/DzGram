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

from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw, types
from ..object import Object


class RichMessageButton(Object):
    """This object represents a button in a rich message.

    Parameters:
        text (``str``):
            Button text.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the Web App that will be launched when the user presses the button.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
            An HTTP URL used to automatically authorize the user.

        copy_text (:obj:`~pyrogram.types.CopyTextButton`, *optional*):
            Description of the button that copies the specified text to the clipboard.

        style (:obj:`~pyrogram.enums.ButtonStyle`, *optional*):
            Style of the button.

        icon_custom_emoji_id (``str``, *optional*):
            Unique identifier of the custom emoji shown before the text of the button.

        disabled (``bool``, *optional*):
            Whether the button is disabled.
    """

    def __init__(
        self,
        text: str = "",
        *,
        callback_data: Optional[Union[str, bytes]] = None,
        url: Optional[str] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        login_url: Optional["types.LoginUrl"] = None,
        copy_text: Optional["types.CopyTextButton"] = None,
        style: Optional["enums.ButtonStyle"] = None,
        icon_custom_emoji_id: Optional[str] = None,
        disabled: Optional[bool] = None,
    ):
        super().__init__()

        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.login_url = login_url
        self.copy_text = copy_text
        self.style = style
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.disabled = disabled

    @staticmethod
    def read(button: "raw.base.TLObject"):
        raw_style = getattr(button, "style", None)
        button_style = None
        icon_custom_emoji_id = None

        if raw_style is not None:
            if raw_style.bg_primary:
                button_style = enums.ButtonStyle.PRIMARY
            elif raw_style.bg_danger:
                button_style = enums.ButtonStyle.DANGER
            elif raw_style.bg_success:
                button_style = enums.ButtonStyle.SUCCESS
            else:
                button_style = enums.ButtonStyle.DEFAULT
            if raw_style.icon:
                icon_custom_emoji_id = str(raw_style.icon)

        return RichMessageButton(
            text=button.text,
            style=button_style,
            icon_custom_emoji_id=icon_custom_emoji_id,
        )

    async def write(self, client: "pyrogram.Client"):
        button = types.InlineKeyboardButton(
            text=self.text,
            icon_custom_emoji_id=self.icon_custom_emoji_id,
            style=self.style,
            callback_data=self.callback_data,
            url=self.url,
            web_app=self.web_app,
            login_url=self.login_url,
            copy_text=self.copy_text,
            disabled=self.disabled,
        )

        return await button.write(client)
