More on Updates
===============

In :doc:`../start/updates` we have seen how to register handlers for the
"official" update types. This page covers the remaining, more advanced topics:
raw updates and groups.

-----

Raw Updates
-----------

DzGram lets you process raw updates exactly as they arrive from Telegram. You
can register a handler for any raw update type using
:meth:`~pyrogram.Client.on_raw_update`:

.. code-block:: python

    from pyrogram import raw

    @app.on_raw_update()
    async def raw(client, update, users, chats):
        if isinstance(update, raw.types.UpdateUserStatus):
            print(update.user_id, update.status)

The callback receives the raw update object plus the dictionaries of users and
chats referenced by the update.

Groups
------

Handlers are executed in *groups*: an integer that defines the order of
execution among handlers of the same update type. Lower-numbered groups run
first; handlers added without an explicit group are assigned to group 0.

.. code-block:: python

    # Runs first
    app.add_handler(MessageHandler(one), group=-1)
    # Default group, runs second
    app.add_handler(MessageHandler(two))
    # Runs last
    app.add_handler(MessageHandler(three), group=2)

Propagation within a group is stopped when a handler returns ``False``; the
update will then be delivered to the next group. This is useful to implement
"middleware" style logic.

Update Delivery
---------------

Incoming updates are dispatched to the registered handlers in dedicated worker
tasks (the number of workers is controlled by the ``workers`` client setting).
Handlers are *not* awaited sequentially across groups: each update is delivered
to every group, and groups run in parallel.
