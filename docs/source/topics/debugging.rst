Debugging
=========

This page collects a few tips and tricks to debug your DzGram applications.

-----

Enable Logging
--------------

DzGram uses Python's standard :mod:`logging` module. Enable it to see what is
happening under the hood:

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.INFO)

To inspect the raw MTProto exchanges (very verbose), set the level to DEBUG:

.. code-block:: python

    logging.getLogger("pyrogram").setLevel(logging.DEBUG)

Known Loggers
-------------

- ``pyrogram`` — the main logger (connection, session, errors).
- ``pyrogram.session.session`` — the session manager.
- ``pyrogram.dispatcher`` — update dispatching.
- ``pyrogram.parser.html`` / ``pyrogram.parser.markdown`` — text parsers.
- ``pyrogram.crypto`` — crypto backend (warpcrypto) messages.

Common Problems
---------------

**"Client has not been started yet"** — you are invoking methods before
:meth:`~pyrogram.Client.start` or outside the ``async with`` block.

**FloodWait errors** — you are hitting rate limits. Check the ``sleep_threshold``
setting and handle :class:`~pyrogram.errors.FloodWait` in your code.

**"There is no current event loop"** — you are mixing sync and async code.
Use :meth:`~pyrogram.Client.run` or ``asyncio.run(main())`` instead of blocking
calls inside coroutines.

**Session file locked** — another instance of your script is using the same
session. Run only one process per session file.
