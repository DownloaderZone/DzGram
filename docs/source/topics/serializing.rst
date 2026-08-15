Serializing
===========

Many DzGram objects (messages, users, chats, ...) can be *serialized* into a
plain Python dictionary and reconstructed back into the original object. This
is useful to persist data, e.g. in a database or a cache.

-----

Serializing an Object
---------------------

Use the :meth:`~pyrogram.types.Object.write` method on any object to obtain its
serializable representation:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")

    async def main():
        async with app:
            message = await app.send_message("me", "Hello!")
            data = message.write()
            print(data)

    app.run()

The resulting dictionary contains only primitive types (``int``, ``str``,
``bool``, ``None``, lists and nested dictionaries), so it can be JSON-encoded
or stored in a database directly.

Deserializing an Object
-----------------------

Use the *classmethod* :meth:`~pyrogram.types.Object.read` on the same class to
reconstruct the object from its dictionary:

.. code-block:: python

    from pyrogram import types

    message = types.Message.read(data)
    print(message.text)

The reconstructed object is fully usable as long as its *client* reference is
set (pass ``client=app`` to :meth:`~pyrogram.types.Object.read` if you need to
invoke bound methods on it).
