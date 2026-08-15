Frequently Asked Questions
==========================

What is DzGram?
---------------

DzGram is a fork of `Pyrogram`_ — an elegant, modern and asynchronous Telegram
MTProto API framework for Python. It is maintained by the Downloader Zone
community and ships with up-to-date Telegram API support (stories, gifts,
topics, business accounts, rich messages, ...).

Why does it import as ``pyrogram``?
-----------------------------------

DzGram is a *drop-in replacement* for Pyrogram: existing code that does
``from pyrogram import Client`` keeps working without changes. The package is
published on PyPI as ``dzgram`` but imports as ``pyrogram``.

Do I need an API key?
---------------------

Yes. Register an application at https://my.telegram.org/apps to obtain the
*api_id* and *api_hash*. Bots instead use a *bot_token* from `@BotFather`_.

Can I use DzGram with a bot account?
------------------------------------

Yes — see :doc:`../start/auth`. Bots have some limitations imposed by Telegram
(e.g. they cannot see the full message history and are rate-limited more
strictly), but all bot-related methods are available.

What is the difference between a session file and a session string?
-------------------------------------------------------------------

The session file (``.session``) is the SQLite storage used by default.
A session string is the same data serialized as a base64 string, usable with
*in-memory* storage — see :doc:`storage-engines`.

Is DzGram stable?
-----------------

DzGram is widely used in production. As with any MTProto framework, keep your
session files secret and handle :class:`~pyrogram.errors.RPCError` properly.

How can I contribute?
---------------------

Check the `contributing guidelines`_ in the repository, and join the
`support group`_ for discussions.

.. _Pyrogram: https://github.com/pyrogram/pyrogram
.. _@BotFather: https://t.me/botfather
.. _contributing guidelines: https://github.com/DownloaderZone/DzGram/blob/master/CONTRIBUTING.md
.. _support group: https://t.me/DzgramDiscussion
