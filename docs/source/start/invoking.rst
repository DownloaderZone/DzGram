Invoking Methods
================

Every method you can invoke is available through the :class:`~pyrogram.Client`
class, so you can easily start working with the API right away after
:doc:`setting up <setup>` and :doc:`authorizing <auth>` your account.

-----

Making API Calls
----------------

DzGram enables you to call both high-level, user-friendly methods (like
:meth:`~pyrogram.Client.send_message` and :meth:`~pyrogram.Client.get_chat_history`)
and low-level raw functions (like ``pyrogram.raw.functions.messages.SendMessage``).

High-level methods take care of parsing the responses into easy-to-use objects
(:obj:`~pyrogram.types.Message`, :obj:`~pyrogram.types.User`, :obj:`~pyrogram.types.Chat`,
...), while raw functions return raw TL objects.

Here is a comparison of the two approaches, both sending the message
"Hi there!" to the chat with username ``haskell``:

.. tab-set::

    .. tab-item:: High-level

        .. code-block:: python

            from pyrogram import Client

            app = Client("my_account")

            async with app:
                await app.send_message("haskell", "Hi there!")

    .. tab-item:: Low-level

        .. code-block:: python

            from pyrogram import Client
            from pyrogram.raw import functions, types

            app = Client("my_account")

            async with app:
                await app.invoke(
                    functions.messages.SendMessage(
                        peer=await app.resolve_peer("haskell"),
                        message="Hi there!",
                        random_id=app.rnd_id(),
                    )
                )

Asynchronous
------------

DzGram is fully asynchronous: every network-bound method must be awaited. This
means the whole :class:`~pyrogram.Client` API surface is *async*, with the
exception of a few pure-python helpers.

If you come from a synchronous background (or from the Bot API), you might want
to read the :doc:`../topics/synchronous` page, which explains how to use DzGram
synchronously as well.

Resolution of Chats
-------------------

High-level methods accept both numeric chat ids and string identifiers such as
usernames, phone numbers or the special values ``"me"`` and ``"self"``. They are
transparently resolved to the internal peer representation before the API call
is made, so you usually don't need to call :meth:`~pyrogram.Client.resolve_peer`
yourself unless you are working with raw functions.

Error Handling
--------------

Errors raised by the API are instances of :obj:`~pyrogram.errors.RPCError`.
DzGram's error system is designed to make it as easy as possible to understand
what went wrong and handle it programmatically. See :doc:`errors` for details.
