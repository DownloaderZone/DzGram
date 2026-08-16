Creating Filters
================

DzGram's filter system is designed to be easily extendable: you can write your
own filters by subclassing the :class:`~pyrogram.filters.Filter` class and
implementing its :meth:`~pyrogram.filters.Filter.__call__` method.

-----

The Filter Class
----------------

A filter is a callable that receives the client and the update, and returns a
boolean-like value (or an awaitable of it). When the returned value is truthy,
the handler is executed; the value is also passed to the handler as the ``filters``
attribute of the update object:

.. code-block:: python

    from pyrogram.filters import Filter


    class IsOwner(Filter):
        def __init__(self, user_id):
            self.user_id = user_id

        async def __call__(self, client, update):
            return update.from_user.id == self.user_id

Filters are meant to be used in combination, so the ``__call__`` method should
return a *truthy* value that can be inspected by combined filters. Keep this in
mind if you need to use the value returned by combined filters.

Merging with Other Filters
--------------------------

Because custom filters are plain :class:`~pyrogram.filters.Filter` instances,
they can be combined with the built-in ones using the ``&``, ``|`` and ``~``
operators:

.. code-block:: python

    app.add_handler(
        MessageHandler(handler, IsOwner(123456789) & filters.private)
    )

Function-based Filters
----------------------

For simple cases you can also create a filter from a plain function:

.. code-block:: python

    from pyrogram import filters


    @filters.create
    def is_weekend(client, message):
        return datetime.now().weekday() >= 5

    @app.on_message(is_weekend)
    async def weekend_handler(client, message):
        await message.reply("Happy weekend!")
