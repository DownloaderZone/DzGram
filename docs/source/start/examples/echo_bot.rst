Echo Bot
========

A bot that echoes every message it receives back to the sender. This example
demonstrates the usage of :doc:`filters <../../topics/use-filters>` and the
:meth:`~pyrogram.Client.on_message` decorator.

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_bot", bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

    @app.on_message(filters.text & filters.private)
    async def echo(client, message):
        await message.reply(message.text)

    app.run()
