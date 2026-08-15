MTProto vs Bot API
==================

DzGram uses the *MTProto* API, the low-level protocol used by Telegram clients
themselves. This is different from the *Bot API* (the HTTP JSON interface
exposed by ``api.telegram.org``), which is what most other bot frameworks use.

-----

Comparison
----------

.. list-table::
    :header-rows: 1

    * - Feature
      - MTProto (DzGram)
      - Bot API
    * - Login as a user
      - Yes
      - No (bots only)
    * - Bots support
      - Yes
      - Yes
    * - Update handling
      - Long polling (built-in)
      - Webhooks / getUpdates
    * - Rate limits
      - Less strict
      - Strict (per-second messages, commands)
    * - Message history access
      - Full (user account)
      - Limited
    * - Media size limits
      - 4 GB (files), 2 GB (bots via upload)
      - 50 MB (via API), 2 GB (via file_id)
    * - Low-level API access
      - Yes (raw functions)
      - No
    * - Protocol
      - Binary (MTProto over TCP/TLS)
      - JSON over HTTPS

Which One to Choose?
--------------------

Use DzGram when you need:

- a **user account** client (automation, personal bots, scraping);
- **full access** to Telegram's API (groups, stories, gifts, rich messages);
- **low-level** control over the protocol;
- freedom from the Bot API's rate limits.

If your goal is a simple bot that must talk to the official Bot API (for
example to integrate with webhooks-based services), the `python-telegram-bot`_
or `aiogram`_ libraries might be a better fit.

.. _python-telegram-bot: https://github.com/python-telegram-bot/python-telegram-bot
.. _aiogram: https://github.com/aiogram/aiogram
