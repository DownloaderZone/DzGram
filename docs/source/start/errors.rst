Error Handling
==============

Errors can be correctly handled with ``try...except`` blocks in order to control
the behaviour of your application. DzGram errors all live inside the
:mod:`~pyrogram.errors` package:

.. code-block:: python

    from pyrogram import errors

-----

RPCError
--------

The father of all errors is named :class:`~pyrogram.errors.RPCError` and is able
to catch all Telegram API related errors. This error is raised every time a
method call against Telegram's API was unsuccessful.

.. code-block:: python

    from pyrogram.errors import RPCError

.. warning::

    Avoid catching this error everywhere, especially when no feedback is given
    (i.e. by logging/printing the full error traceback), because it makes it
    impossible to understand what went wrong.

Error Categories
----------------

The ``RPCError`` packs together all the possible errors Telegram could raise,
but to make things tidier, DzGram provides categories of errors, which are named
after the common HTTP errors and are subclassed from the ``RPCError``:

.. code-block:: python

    from pyrogram.errors import BadRequest, Forbidden, ...

- ``303 - SeeOther``
- ``400 - BadRequest``
- ``401 - Unauthorized``
- ``403 - Forbidden``
- ``406 - NotAcceptable``
- ``420 - Flood``
- ``500 - InternalServerError``

Single Errors
-------------

For a fine-grained control over every single error, DzGram also exposes errors
that deal each with a specific problem. These errors are subclasses of their
corresponding category:

.. code-block:: python

    from pyrogram.errors import FloodWait, MessageIdInvalid, ...

Here is a list of the most common ones:

- ``400 - MessageIdInvalid``: The message id is invalid.
- ``400 - UsernameNotOccupied``: The username is not occupied by anyone.
- ``400 - PeerIdInvalid``: The chat id/username is invalid.
- ``403 - MessageAuthorRequired``: No message with the given ID was found.
- ``420 - FloodWait``: A wait of X seconds is required before you can continue.
- ``500 - InternalServerError``: An internal server error occurred while processing your request.

Every specific error also carries the code, the message, the *x* error
identifier and, for ``FloodWait``, the number of seconds to wait:

.. code-block:: python

    import asyncio
    from pyrogram.errors import FloodWait

    try:
        await app.send_message("me", "Hello!")
    except FloodWait as e:
        print(f"Rate limited: wait {e.value} seconds")
        await asyncio.sleep(e.value)

Unknown Errors
--------------

In case of an unknown error, DzGram raises a generic ``500 - InternalServerError``
with the error code and identifier in the message, so you can always inspect the
traceback and report the problem.

.. code-block:: python

    from pyrogram.errors import InternalServerError

    try:
        await app.get_messages("me", 0)
    except InternalServerError as e:
        print(e)  # prints something like: InternalServerError [500 INTERNAL]: ...
