Client Settings
===============

The :class:`~pyrogram.Client` class exposes a number of settings that change
the behaviour of your application. This page summarizes the most useful ones;
see the :doc:`../api/client` reference for the complete list of parameters.

-----

Session Name & Storage
----------------------

.. code-block:: python

    app = Client(
        "my_account",              # name of the session file
        session_string="...",      # use an in-memory session instead
        storage_engine=MyStorage,  # custom storage backend
        workdir=".",               # where the session file is stored
    )

In-memory sessions (``session_string``) are not written to disk at all, which
is useful for ephemeral deployments. See :doc:`storage-engines`.

API Credentials
---------------

.. code-block:: python

    app = Client(
        "my_account",
        api_id=12345,
        api_hash="0123456789abcdef0123456789abcdef",
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",  # for bots
        app_version="1.0.0",
        device_model="My Device",
        system_version="Linux",
        lang_code="en",
    )

Proxy
-----

.. code-block:: python

    app = Client(
        "my_account",
        proxy={
            "scheme": "socks5",
            "hostname": "127.0.0.1",
            "port": 1080,
            "username": "user",
            "password": "pass",
        },
    )

See :doc:`proxy` for more details.

Network Tuning
--------------

.. code-block:: python

    app = Client(
        "my_account",
        workers=16,                    # number of update handling workers
        max_concurrent_transmissions=1,  # concurrent outgoing requests
        sleep_threshold=60,            # sleep before retrying flood waits
        no_updates=False,              # True to skip updates handling
        takeout=False,                 # enable takeout sessions
        ipv6=False,                    # prefer IPv6
    )

Device Settings
---------------

.. code-block:: python

    app = Client(
        "my_account",
        device_model="MyDevice",
        system_version="MyOS",
        app_version="1.0.0",
        lang_code="en",
        system_lang_code="en",
    )

Parse Modes
-----------

.. code-block:: python

    app = Client(
        "my_account",
        parse_mode=enums.ParseMode.HTML,  # default parse mode for all texts
        disable_web_page_preview=True,    # default link preview behaviour
    )

The default *parse_mode* is applied to every method call that accepts a
*parse_mode* argument unless explicitly overridden.
