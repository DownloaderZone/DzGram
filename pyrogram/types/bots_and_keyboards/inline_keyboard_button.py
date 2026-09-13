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


class InlineKeyboardButton(Object):
    """One button of an inline keyboard.

    Exactly one of the fields other than ``text``, ``icon_custom_emoji_id``, and ``style`` must be used to specify the type of the button.

    Parameters:
        text (``str``):
            Label text on the button.

        icon_custom_emoji_id (``str``, *optional*):
            Unique identifier of the custom emoji shown before the text of the button. Can only be used by bots that purchased additional usernames on Fragment or in the messages directly sent by the bot to private, group and supergroup chats if the owner of the bot has a Telegram Premium subscription..

        style (:obj:`~pyrogram.enums.ButtonStyle`, *optional*):
            Style of the button.
            If omitted, then an app-specific style is used.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        user_id (``int``, *optional*):
            User id, for links to the user profile.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the `Web App <https://core.telegram.org/bots/webapps>`_ that will be launched when the user
            presses the button. The Web App will be able to send an arbitrary message on behalf of the user using the
            method :meth:`~pyrogram.Client.answer_web_app_query`. Available only in private chats between a user and the
            bot.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
             An HTTP URL used to automatically authorize the user. Can be used as a replacement for
             the `Telegram Login Widget <https://core.telegram.org/widgets/login>`_.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert
            the bot's username and the specified inline query in the input field. Can be empty, in which case just
            the bot's username will be inserted.Note: This offers an easy way for users to start using your bot in
            inline mode when they are currently in a private chat with it. Especially useful when combined with
            switch_pm… actions – in this case the user will be automatically returned to the chat they switched from,
            skipping the chat selection screen.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username and the specified inline query in the current
            chat's input field. Can be empty, in which case only the bot's username will be inserted.This offers a
            quick way for the user to open your bot in inline mode in the same chat - good for selecting something
            from multiple options.

        switch_inline_query_chosen_chat (:obj:`~pyrogram.types.SwitchInlineQueryChosenChat`, *optional*):
            If set, pressing the button will prompt the user to select one of their chats of the specified type, open that chat and insert the bot's username and the specified inline query in the input field

        copy_text (:obj:`~pyrogram.types.CopyTextButton`, *optional*):
            Description of the button that copies the specified text to the clipboard.

        callback_game (:obj:`~pyrogram.types.CallbackGame`, *optional*):
            Description of the game that will be launched when the user presses the button.

            .. note::

                This type of button **must** always be the first button in the first row.

        pay (``bool``, *optional*):
            Specify True, to send a Pay button. Substrings "⭐" and "XTR" in the buttons's text will be replaced with a Telegram Star icon.

            .. note:

                This type of button **must** always be the first button in the first row and can only be used in invoice messages.

        callback_data_with_password (``bytes``, *optional*):
            A button that asks for the 2-step verification password of the current user and then sends a callback query to a bot Data to be sent to the bot via a callback query.

        disabled (``bool``, *optional*):
            True, if the button is disabled and cannot be pressed.

    """

    def __init__(
        self,
        text: str,
        icon_custom_emoji_id: Optional[str] = None,
        style: Optional["enums.ButtonStyle"] = enums.ButtonStyle.DEFAULT,
        *,
        url: Optional[str] = None,
        user_id: Optional[int] = None,
        callback_data: Optional[Union[str, bytes]] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        login_url: Optional["types.LoginUrl"] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        switch_inline_query_chosen_chat: Optional["types.SwitchInlineQueryChosenChat"] = None,
        copy_text: Optional["types.CopyTextButton"] = None,
        callback_game: Optional["types.CallbackGame"] = None,
        pay: Optional[bool] = None,
        callback_data_with_password: Optional[bytes] = None,
        disabled: Optional[bool] = None,
    ):
        super().__init__()

        self.text = str(text)
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.login_url = login_url
        self.user_id = user_id
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.switch_inline_query_chosen_chat = switch_inline_query_chosen_chat
        self.callback_game = callback_game
        self.pay = pay
        self.copy_text = copy_text
        self.callback_data_with_password = callback_data_with_password
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.style = style
        self.disabled = disabled

    @staticmethod
    def _read_style(b: "raw.types.KeyboardInlineButton"):
        raw_style: "raw.types.KeyboardButtonStyle" = getattr(b, "style", None)
        button_style = enums.ButtonStyle.DEFAULT
        icon_custom_emoji_id = None

        if raw_style is not None:
            if raw_style.bg_primary:
                button_style = enums.ButtonStyle.PRIMARY
            elif raw_style.bg_danger:
                button_style = enums.ButtonStyle.DANGER
            elif raw_style.bg_success:
                button_style = enums.ButtonStyle.SUCCESS
            if raw_style.icon:
                icon_custom_emoji_id = str(raw_style.icon)

        return button_style, icon_custom_emoji_id

    @staticmethod
    def read(b: "raw.types.KeyboardInlineButton"):
        if not isinstance(b, raw.types.KeyboardInlineButton):
            return None

        disabled = False
        button_style, icon_custom_emoji_id = InlineKeyboardButton._read_style(b)
        t = b.type

        if isinstance(t, raw.types.InlineButtonTypeDisabled):
            disabled = True
            return InlineKeyboardButton(
                text=b.text,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
                disabled=disabled,
            )

        if isinstance(t, raw.types.InlineButtonTypeCallback):
            # Try decode data to keep it as string, but if fails, fallback to bytes so we don't lose any information,
            # instead of decoding by ignoring/replacing errors.
            try:
                data = t.data.decode()
            except UnicodeDecodeError:
                data = t.data

            if getattr(t, "requires_password", None):
                return InlineKeyboardButton(
                    text=b.text,
                    callback_data_with_password=data,
                    style=button_style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                )

            return InlineKeyboardButton(
                text=b.text,
                callback_data=data,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeUrl):
            return InlineKeyboardButton(
                text=b.text,
                url=t.url,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeUrlAuth):
            return InlineKeyboardButton(
                text=b.text,
                login_url=types.LoginUrl.read(t),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeUserProfile):
            return InlineKeyboardButton(
                text=b.text,
                user_id=t.user_id,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeSwitchInline):
            if getattr(t, "same_peer", None):
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query_current_chat=t.query,
                    style=button_style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                )
            elif getattr(t, "peer_types", None):
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat.read(t),
                    style=button_style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                )
            else:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query=t.query,
                    style=button_style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                )

        if isinstance(t, raw.types.InlineButtonTypeGame):
            return InlineKeyboardButton(
                text=b.text,
                callback_game=types.CallbackGame(),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeWebView):
            return InlineKeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(
                    url=t.url
                ),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeBuy):
            return InlineKeyboardButton(
                text=b.text,
                pay=True,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(t, raw.types.InlineButtonTypeCopy):
            return InlineKeyboardButton(
                text=b.text,
                copy_text=types.CopyTextButton(
                    text=t.copy_text
                ),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        return InlineKeyboardButton(
            text=b.text,
            style=button_style,
            icon_custom_emoji_id=icon_custom_emoji_id,
        )

    async def write(self, client: "pyrogram.Client"):
        raw_style = raw.types.KeyboardButtonStyle(
            bg_primary=self.style == enums.ButtonStyle.PRIMARY,
            bg_danger=self.style == enums.ButtonStyle.DANGER,
            bg_success=self.style == enums.ButtonStyle.SUCCESS,
            icon=int(self.icon_custom_emoji_id) if self.icon_custom_emoji_id else None
        )

        if self.disabled:
            button_type = raw.types.InlineButtonTypeDisabled()
        elif self.callback_data_with_password is not None:
            if isinstance(self.callback_data_with_password, str):
                raise ValueError(
                    "This is not supported"
                )
            button_type = raw.types.InlineButtonTypeCallback(
                data=self.callback_data_with_password,
                requires_password=True,
            )

        elif self.callback_data is not None:
            # Telegram only wants bytes, but we are allowed to pass strings too, for convenience.
            data = bytes(self.callback_data, "utf-8") if isinstance(self.callback_data, str) else self.callback_data

            button_type = raw.types.InlineButtonTypeCallback(data=data)

        elif self.url is not None:
            button_type = raw.types.InlineButtonTypeUrl(url=self.url)

        elif self.login_url is not None:
            button_type = await self.login_url.write(
                bot=await client.resolve_peer(self.login_url.bot_username or "self"),
            )

        elif self.user_id is not None:
            button_type = raw.types.InputInlineButtonTypeUserProfile(
                user_id=await client.resolve_peer(self.user_id),
            )

        elif self.switch_inline_query is not None:
            button_type = raw.types.InlineButtonTypeSwitchInline(query=self.switch_inline_query)

        elif self.switch_inline_query_current_chat is not None:
            button_type = raw.types.InlineButtonTypeSwitchInline(
                query=self.switch_inline_query_current_chat,
                same_peer=True,
            )

        elif self.switch_inline_query_chosen_chat is not None:
            button_type = self.switch_inline_query_chosen_chat.write()

        elif self.callback_game is not None:
            button_type = raw.types.InlineButtonTypeGame()

        elif self.web_app is not None:
            button_type = raw.types.InlineButtonTypeWebView(url=self.web_app.url)

        elif self.pay:
            button_type = raw.types.InlineButtonTypeBuy()

        elif self.copy_text is not None:
            button_type = raw.types.InlineButtonTypeCopy(copy_text=self.copy_text.text)

        else:
            raise ValueError(
                "InlineKeyboardButton must have at least one of url, callback_data, "
                "switch_inline_query, web_app, login_url, user_id, callback_game, pay or copy_text"
            )

        return raw.types.KeyboardInlineButton(
            text=self.text,
            type=button_type,
            style=raw_style
        )
