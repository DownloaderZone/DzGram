Callback Queries
================

This example demonstrates how to handle callback queries from inline keyboards
using the :meth:`~pyrogram.Client.on_callback_query` decorator and answer them
with :meth:`~pyrogram.types.CallbackQuery.answer`.

.. code-block:: python

    from pyrogram import Client, filters
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    app = Client("my_bot", bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

    @app.on_message(filters.command("start"))
    async def start(client, message):
        await message.reply(
            "What do you want to do?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Like", callback_data="like"),
                        InlineKeyboardButton("Dislike", callback_data="dislike"),
                    ]
                ]
            )
        )

    @app.on_callback_query()
    async def on_callback(client, callback_query):
        await callback_query.answer(f"You pressed: {callback_query.data}")
        await callback_query.message.reply(f"Choice: {callback_query.data}")

    app.run()
