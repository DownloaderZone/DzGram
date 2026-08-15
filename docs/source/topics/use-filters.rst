Using Filters
=============

Filters are a powerful tool that allows you to filter updates to handle only
the ones you are interested in. They are used together with the handlers
decorators to restrict which updates reach your callback functions.

-----

Basics
------

Filters are attached to the decorators with the pipe ``|`` operator to combine
them, and the ampersand ``&`` operator to compose them:

.. code-block:: python

    from pyrogram import filters

    @app.on_message(filters.command("start") & filters.private)
    async def start(client, message):
        await message.reply("Hello!")

    @app.on_message(filters.text | filters.media)
    async def text_or_media(client, message):
        print(message.text or "media message")

The ``~`` operator negates a filter:

.. code-block:: python

    @app.on_message(~filters.private)
    async def not_private(client, message):
        print(f"Message in {message.chat.type}")

Common Filters
--------------

Here is a list of the most commonly used filters:

- ``filters.command("start", "help")`` — messages starting with a command
- ``filters.text`` — text messages
- ``filters.media`` — messages with any media
- ``filters.photo``, ``filters.video``, ``filters.audio``, ``filters.document``,
  ``filters.animation``, ``filters.sticker``, ``filters.voice``, ``filters.video_note``
- ``filters.private``, ``filters.group``, ``filters.channel`` — chat type
- ``filters.user("username")`` / ``filters.users([123, 456])`` — from certain users
- ``filters.chat("username")`` / ``filters.chats([123, 456])`` — in certain chats
- ``filters.regex(r"pattern")`` — regex match against the text
- ``filters.edited`` — edited messages
- ``filters.deleted`` — deleted messages
- ``filters.reply`` — messages that are replies
- ``filters.forwarded`` — forwarded messages
- ``filters.via_bot`` — messages sent via a bot
- ``filters.bot`` / ``filters.creator`` / ``filters.admin`` — sender role
- ``filters.new_chat_members``, ``filters.left_chat_member`` — member updates

.. note::

    Filters can be created dynamically (e.g. ``filters.user("me")``) or reused
    across handlers. When a filter takes arguments, a *new* filter is created
    each time it is called.

You can find the complete list in the :doc:`../api/filters/index` reference.
