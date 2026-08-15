Storage Engines
===============

DzGram stores the session data (authorization key, user/bot identity, DC
information) in a *storage engine*. By default a SQLite-backed file storage is
used, but you can implement your own to store sessions in memory, databases,
or wherever you like.

-----

File Storage
------------

The default engine writes a single ``.session`` file next to your script (or in
the *workdir*):

.. code-block:: python

    app = Client("my_account")  # creates my_account.session

In-memory Storage
-----------------

Pass a *session_string* to keep everything in memory: no file is ever written,
and you can obtain the serialized session with
:meth:`~pyrogram.Client.export_session_string`:

.. code-block:: python

    app = Client("my_account", session_string="...")
    string = await app.export_session_string()

The exported string can be shared across devices and used to log in without
re-entering the credentials.

Custom Storage
--------------

Implement the :class:`~pyrogram.storage.Storage` interface and pass it via the
*storage_engine* parameter:

.. code-block:: python

    from pyrogram.storage import Storage


    class MyStorage(Storage):
        def __init__(self, name):
            super().__init__(name)

        async def open(self): ...
        async def save(self): ...
        async def delete(self): ...
        async def update_peers(self, peers): ...
        async def get_peer_by_id(self, peer_id): ...
        async def get_peer_by_username(self, username): ...
        async def get_peer_by_phone_number(self, phone_number): ...

    app = Client("my_account", storage_engine=MyStorage)

Take a look at the :doc:`../api/storage` reference for the full interface.
