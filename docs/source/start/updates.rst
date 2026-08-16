Updates Handling
================

We have just :doc:`set up <setup>` a project and :doc:`authorized <auth>` ourselves.
In this page we'll see how to make our app react to events happening in Telegram.

-----

Defining Updates
----------------

Updates are events that happen in your Telegram account (incoming messages,
new members joining a group, bot commands, etc.). To handle these updates you
define callback functions using the :meth:`~pyrogram.Client.on_message` (or
:meth:`~pyrogram.Client.on_edited_message`, :meth:`~pyrogram.Client.on_callback_query`,
...) decorators. The decorated function is called whenever a new update of that
type arrives.

The function must accept at least two arguments: the *client* (an instance of
:class:`~pyrogram.Client`) and the *update* (an instance of
:obj:`~pyrogram.types.Message`, :obj:`~pyrogram.types.CallbackQuery`, ...).

.. code-block:: python

    from pyrogram import Client, filters

    @app.on_message()  # Decorating with no arguments means: all messages
    async def my_handler(client, message):
        print(message)

    @app.on_edited_message()
    async def my_edited_handler(client, edited_message):
        print(edited_message)

Filters
-------

Use :doc:`filters <../topics/use-filters>` to control which updates a handler
receives. Filters are attached to the decorator and are checked against each
incoming update; if the filter matches, the handler is executed:

.. code-block:: python

    from pyrogram import Client, filters

    @app.on_message(filters.command("start") & filters.private)
    async def start(client, message):
        await message.reply("Hello! I'm a bot.")

The decorated handlers can be registered at any time, even after the client has
started.

Registering Handlers Without Decorators
---------------------------------------

Handlers can also be registered manually by instantiating a handler object and
passing it to :meth:`~pyrogram.Client.add_handler`:

.. code-block:: python

    from pyrogram import Client, filters
    from pyrogram.handlers import MessageHandler

    async def hello(client, message):
        await message.reply("Hello!")

    app.add_handler(MessageHandler(hello, filters.command("start")))

Grouping Handlers
-----------------

Handlers are executed in groups, in the order they were added. You can pass a
``group`` number to :meth:`~pyrogram.Client.add_handler` to control the order:
handlers in lower-numbered groups run first.

.. code-block:: python

    app.add_handler(MessageHandler(one), group=1)
    app.add_handler(MessageHandler(two), group=8)

Stopping Propagation
--------------------

Handlers in the same group are executed in order until one of them stops the
propagation of the update. This is done by returning ``False`` from the handler:

.. code-block:: python

    @app.on_message(filters.command("start"))
    async def start(client, message):
        await message.reply("Hello!")
        return False  # Stops the propagation of this update to the next handler

See :doc:`../topics/more-on-updates` for more advanced topics on updates
handling, such as raw updates.
