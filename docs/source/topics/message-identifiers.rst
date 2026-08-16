Message Identifiers
===================

Telegram uses 64-bit identifiers for messages. Depending on how a message was
created, its identifier may be *local* (assigned by the client) or *global*
(assigned by the server), and this matters when you want to refer to a message
later.

-----

Local vs Global Identifiers
---------------------------

- **Local IDs** are used by scheduled messages before they are sent. When you
  schedule a message with :meth:`~pyrogram.Client.send_message` (passing
  ``schedule_date``), the returned :class:`~pyrogram.types.Message` carries a
  local, negative or zero-based identifier until the server processes it.
- **Global IDs** are the real, monotonically increasing identifiers assigned to
  messages delivered to a chat.

For messages sent regularly (not scheduled), the identifier returned is already
the global one and can be used freely with methods like
:meth:`~pyrogram.Client.delete_messages` or
:meth:`~pyrogram.Client.edit_message_text`.

Scheduled Messages
------------------

Scheduled messages (and, starting December 1, 2024, videos automatically
scheduled by the server until they are re-encoded) may expose a local
identifier. Before using such an identifier in methods that reference messages,
make sure the message is actually sent (e.g. check the ``scheduled`` property
or wait for the delivery) — otherwise the reference will not be found by the
server.

Practical Advice
----------------

- Prefer :class:`~pyrogram.types.Message` objects you received or sent
  yourself.
- When storing identifiers for later use (e.g. in a database), prefer the
  global identifier of messages that are already in the chat.
- For message history, iterate with :meth:`~pyrogram.Client.get_chat_history`
  and use the returned objects directly.
