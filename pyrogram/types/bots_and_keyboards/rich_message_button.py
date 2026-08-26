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
    def read(button: "raw.types.RichMessageButton"):
        raw_style: "raw.types.KeyboardButtonStyle" = button.style
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
            callback_data=button.callback_data,
            url=button.url,
            web_app=types.WebAppInfo(url=button.web_app.url) if button.web_app else None,
            login_url=types.LoginUrl.read(button.login_url) if button.login_url else None,
            copy_text=types.CopyTextButton(text=button.copy_text) if button.copy_text else None,
            style=button_style,
            icon_custom_emoji_id=icon_custom_emoji_id,
            disabled=button.disabled or None,
        )

    async def write(self, client: "pyrogram.Client"):
        raw_style = None

        if self.style is not None:
            raw_style = raw.types.KeyboardButtonStyle(
                bg_primary=self.style == enums.ButtonStyle.PRIMARY,
                bg_danger=self.style == enums.ButtonStyle.DANGER,
                bg_success=self.style == enums.ButtonStyle.SUCCESS,
                icon=int(self.icon_custom_emoji_id) if self.icon_custom_emoji_id else None,
            )

        return raw.types.RichMessageButton(
            text=self.text,
            callback_data=self.callback_data,
            url=self.url,
            web_app=raw.types.DataJSON(data=self.web_app.url) if self.web_app else None,
            login_url=await self.login_url.write(
                bot=await client.resolve_peer(self.login_url.bot_username or "self"),
            ) if self.login_url else None,
            copy_text=self.copy_text.text if self.copy_text else None,
            style=raw_style,
            disabled=self.disabled or False,
        )
