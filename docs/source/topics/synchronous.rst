Synchronous Usage
=================

DzGram is fully asynchronous, but it also offers a simple way to use it
synchronously: the :meth:`~pyrogram.Client.run` method.

-----

The run() Method
----------------

Calling :meth:`~pyrogram.Client.run` without arguments blocks the current
thread and runs an internal event loop until the client is stopped:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")
    app.run()

With a coroutine argument, the coroutine is awaited inside the loop after the
client starts and the result is returned:

.. code-block:: python

    async def main():
        await app.send_message("me", "Hello!")

    app.run(main())

Composing with Other Libraries
------------------------------

If you need to use synchronous, blocking libraries (like ``requests`` or
``sqlite3``) inside your asynchronous code, you can offload the work to a
thread pool with ``asyncio.to_thread``. Conversely, blocking functions that
must run inside the event loop will block the whole application: be careful.
