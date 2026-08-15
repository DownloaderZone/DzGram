Test Servers
============

Telegram provides an alternative, isolated environment for developers to test
their applications against: the *test servers*. Accounts and bots on the test
servers are completely separate from the production ones.

-----

Using the Test Servers
----------------------

Create the client with ``test_mode=True``:

.. code-block:: python

    app = Client(
        "my_test_account",
        api_id=12345,
        api_hash="0123456789abcdef0123456789abcdef",
        test_mode=True,
    )

In test mode:

- a separate session file is used (suffixed with ``.test``);
- you authorize with a test phone number (e.g. ``99966`` + 5 random digits);
- test bots are created with `@BotFather`_ on the test servers;
- peer identifiers are not shared with production.

.. note::

    In test mode there is no production data, so anything you do is safe.
    Remember to create the client with ``test_mode=True`` in production code
    paths too if you switch between the two environments.

.. _@BotFather: https://t.me/botfather
