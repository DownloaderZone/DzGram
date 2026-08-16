Install Guide
=============

Being a modern Python framework, DzGram requires an up to date version of
Python 3 to be installed in your system. We recommend using the latest
versions of both Python 3 and pip.

-----

Install DzGram
--------------

.. code-block:: bash

    $ pip install dzgram

Bleeding Edge
-------------

You can install the development version directly from the repository:

.. code-block:: bash

    $ pip install git+https://github.com/DownloaderZone/DzGram.git

Verifying
---------

To verify that DzGram is correctly installed, open a Python shell and import it.
If no error shows up you are good to go.

.. parsed-literal::

    >>> from pyrogram import __version__
    >>> __version__
    '2.2.28'
