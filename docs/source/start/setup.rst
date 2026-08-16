Project Setup
=============

We have just :doc:`installed DzGram <../intro/install>`. In this page we'll
discuss what you need to do in order to set up a project with the framework.

-----

API Key
-------

The first step requires you to obtain a valid Telegram API key (an *api_id* and
*api_hash* pair):

#. Visit https://my.telegram.org/apps and log in with your Telegram account.
#. Fill out the form with your details and register a new Telegram application.
#. Done. The API key consists of two parts: **api_id** and **api_hash**. Keep it secret.

.. note::

    The API key defines a token for a Telegram *application* you are going to build.
    This means that you are able to authorize multiple users or bots with a single API key.

Configuration
-------------

Having the API key from the previous step in handy, we can now begin to configure
a DzGram project: pass your API key to DzGram by using the *api_id* and *api_hash*
parameters of the :class:`~pyrogram.Client` class:

.. code-block:: python

    from pyrogram import Client

    api_id = 12345
    api_hash = "0123456789abcdef0123456789abcdef"

    app = Client("my_account", api_id=api_id, api_hash=api_hash)

The first parameter is a name for the client, which is used to identify the
session file (``my_account.session``) that stores the authorization data.

The two other parameters are the API key, as obtained in the previous step.

.. note::

    The Client class also accepts a *session_string* parameter to use an in-memory
    session instead of a file, as well as a *storage_engine* parameter to plug in
    custom storage backends. See :doc:`../topics/storage-engines`.

Your First Project
------------------

Create a new file named ``hello.py`` in the same directory and paste the
following code:

.. code-block:: python

    from pyrogram import Client

    api_id = 12345
    api_hash = "0123456789abcdef0123456789abcdef"

    async def main():
        async with Client("my_account", api_id, api_hash) as app:
            await app.send_message("me", "Greetings from **DzGram**!")


    Client("my_account", api_id, api_hash).run()  # or: asyncio.run(main())

This is the minimal working project that sends a message to your Saved
Messages. Take a look at :doc:`auth` for more details about the authorization
process.
