Inline Queries
==============

This example shows how to answer inline queries — queries users send to your bot
by typing ``@your_bot <query>`` in any chat — using the
:meth:`~pyrogram.Client.on_inline_query` decorator and
:meth:`~pyrogram.Client.answer_inline_query`.

.. code-block:: python

    from pyrogram import Client, types

    app = Client("my_bot", bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

    @app.on_inline_query()
    async def inline_query(client, inline_query):
        results = [
            types.InlineQueryResultArticle(
                title="Hello!",
                input_message_content=types.InputTextMessageContent(
                    "Hello from **DzGram**!"
                )
            ),
            types.InlineQueryResultArticle(
                title="Echo query",
                input_message_content=types.InputTextMessageContent(
                    inline_query.query
                )
            ),
        ]

        await client.answer_inline_query(
            inline_query.id,
            results,
            cache_time=1,
        )

    app.run()
