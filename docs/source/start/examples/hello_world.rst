Hello World
===========

This is a very basic example that demonstrates how to send a message to your
Saved Messages using the :meth:`~pyrogram.Client.send_message` method.

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")

    async def main():
        async with app:
            await app.send_message("me", "Greetings from **DzGram**!")

    app.run()
