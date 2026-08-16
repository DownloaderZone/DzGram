Get Chat History
================

This example demonstrates how to retrieve the message history of a chat and
iterate over it with :meth:`~pyrogram.Client.get_chat_history`.

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")

    async def main():
        async with app:
            async for message in app.get_chat_history("me"):
                print(message.id, message.text)

    app.run()
