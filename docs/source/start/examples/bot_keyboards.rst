Bot Keyboards
=============

This example shows how to send a message with a reply keyboard and an inline
keyboard attached, using :obj:`~pyrogram.types.ReplyKeyboardMarkup` and
:obj:`~pyrogram.types.InlineKeyboardMarkup`.

.. code-block:: python

    from pyrogram import Client, filters
    from pyrogram.types import (
        InlineKeyboardMarkup,
        InlineKeyboardButton,
        ReplyKeyboardMarkup,
    )

    app = Client("my_bot", bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

    @app.on_message(filters.command("start"))
    async def start(client, message):
        await message.reply(
            "Choose an option:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Website", url="https://github.com/DownloaderZone/DzGram"),
                        InlineKeyboardButton("Help", callback_data="help"),
                    ],
                    [InlineKeyboardButton("About", callback_data="about")],
                ]
            )
        )

    @app.on_message(filters.command("keyboard"))
    async def keyboard(client, message):
        await message.reply(
            "Here is a custom reply keyboard:",
            reply_markup=ReplyKeyboardMarkup(
                [["Yes"], ["No"], ["Maybe"]],
                resize_keyboard=True,
            )
        )

    app.run()
