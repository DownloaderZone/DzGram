Authorization
=============

Once a :doc:`project is set up <setup>`, you will still have to follow a few
steps before you can actually use DzGram to make API calls. This section
provides all the information you need in order to authorize yourself as a
user or a bot.

-----

User Authorization
------------------

In order to use the API, Telegram requires that users be authorized via their
phone numbers. DzGram automatically manages this process: all you need to do is
create an instance of the :class:`~pyrogram.Client` class by passing it a
``name`` of your choice (e.g. "my_account") and call the
:meth:`~pyrogram.Client.run` method:

.. code-block:: python

    from pyrogram import Client

    api_id = 12345
    api_hash = "0123456789abcdef0123456789abcdef"

    app = Client("my_account", api_id=api_id, api_hash=api_hash)

    app.run()

This starts an interactive shell asking you to input your **phone number**,
including your `Country Code`_ (the plus ``+`` and minus ``-`` symbols can be
omitted) and the **phone code** you will receive in your already authorized
devices or via SMS:

.. code-block:: text

    Enter phone number: +1-123-456-7890
    Is "+1-123-456-7890" correct? (y/n): y
    Enter phone code: 12345
    Logged in successfully

After successfully authorizing yourself, a new file called ``my_account.session``
will be created, allowing DzGram to execute API calls with your identity.
This file is the proof of your identity and must be kept safe: anyone who gets
it can act on your behalf.

.. _Country Code: https://en.wikipedia.org/wiki/List_of_country_calling_codes

Bot Authorization
-----------------

Bots are a special kind of users that do not need a phone number to authorize.
Instead, they are authorized via an authentication *token*.

You can create a new bot and obtain its token from `@BotFather`_.

Once you have the token, authorization is straightforward: pass the token as a
parameter of the :class:`~pyrogram.Client` class:

.. code-block:: python

    from pyrogram import Client

    app = Client(
        "my_bot",
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    )

    app.run()

.. note::

    Bots can only interact with users and groups they are added to, and they
    can only contact users who write them first. Bots also have a limit on
    outgoing messages and cannot access the message history of chats in some
    cases. See the `Bots FAQ`_ for more details.

.. _@BotFather: https://t.me/botfather
.. _Bots FAQ: https://core.telegram.org/bots/faq

The run() Method
----------------

The :meth:`~pyrogram.Client.run` method is a convenience that starts the client
(connecting to Telegram), runs the given coroutine (or blocks forever, if none
is given) and finally stops the client.

When you need more control — for example to run multiple clients concurrently —
use the client as an asynchronous context manager or call the
:meth:`~pyrogram.Client.start` and :meth:`~pyrogram.Client.stop` methods
manually:

.. code-block:: python

    import asyncio
    from pyrogram import Client

    async def main():
        app = Client("my_account", api_id, api_hash)
        await app.start()
        await app.send_message("me", "Hello!")
        await app.stop()

    asyncio.run(main())
