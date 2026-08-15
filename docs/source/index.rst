DzGram's documentation
======================

`DzGram`_ is an elegant, modern and asynchronous Telegram MTProto API framework
for Python — a fork of `Pyrogram`_ maintained by the Downloader Zone community.
It enables you to easily interact with the main Telegram API through a user
account (custom client) or a bot identity (bot API alternative) using Python.

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")

    @app.on_message(filters.private)
    async def hello(client, message):
        await message.reply("Hello from DzGram!")

    app.run()

.. toctree::
    :maxdepth: 2
    :caption: Introduction

    intro/install
    intro/quickstart

.. toctree::
    :maxdepth: 2
    :caption: Getting Started

    start/setup
    start/auth
    start/invoking
    start/updates
    start/errors
    start/examples/index

.. toctree::
    :maxdepth: 2
    :caption: API Reference

    api/index
    api/client
    api/methods/index
    api/types/index
    api/bound-methods/index
    api/enums/index
    api/filters/index
    api/handlers/index
    api/errors/index
    api/raw/index

.. toctree::
    :maxdepth: 2
    :caption: Topics

    topics/rich-text
    topics/text-formatting
    topics/use-filters
    topics/create-filters
    topics/client-settings
    topics/synchronous
    topics/more-on-updates
    topics/storage-engines
    topics/serializing
    topics/proxy
    topics/test-servers
    topics/mtproto-vs-botapi
    topics/message-identifiers
    topics/debugging
    topics/faq

.. _DzGram: https://github.com/DownloaderZone/DzGram
.. _Pyrogram: https://github.com/pyrogram/pyrogram
