Proxy
=====

DzGram supports HTTP and SOCKS5 proxies through the *proxy* parameter of the
:class:`~pyrogram.Client` class.

-----

Usage
-----

.. code-block:: python

    app = Client(
        "my_account",
        proxy={
            "scheme": "socks5",          # "socks4", "socks5" or "http"
            "hostname": "127.0.0.1",
            "port": 1080,
            "username": "user",          # optional
            "password": "pass",          # optional
        },
    )

You can also pass the proxy settings as a ``socks.Socks5Proxy`` object or use
the environment variables ``HTTPS_PROXY`` / ``HTTP_PROXY`` / ``ALL_PROXY``,
which are honored automatically.

.. note::

    The *pysocks* package is required for SOCKS proxies and is installed by
    default with DzGram.
