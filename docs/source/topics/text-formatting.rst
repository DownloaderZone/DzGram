Text Formatting
===============

DzGram uses a custom Markdown dialect for text formatting which adds some unique
features that make writing styled texts easier in both Markdown and HTML. You
can send sophisticated text messages and media captions using a variety of
decorations that can also be nested in order to combine multiple styles
together.

-----

Basic Styles
------------

The following is a list of the basic styles currently supported by DzGram.

- **bold**
- *italic*
- ~~strike~~
- __underline__
- ||spoiler||
- `text URL <https://pyrogram.org>`_
- user text mention
- ``inline fixed-width code``
- pre-formatted fixed-width code blocks (with optional language)

Markdown Style
--------------

To strictly use this mode, pass ``enums.ParseMode.MARKDOWN`` to the
*parse_mode* parameter. Use the following syntax in your message:

.. code-block:: text

    **bold**

    __italic__

    --underline--

    ~~strike~~

    ||spoiler||

    [text URL](https://pyrogram.org)

    text user mention

    `inline fixed-width code`

    ```python
    pre-formatted fixed-width code block with language
    ```

HTML Style
----------

To strictly use this mode, pass ``enums.ParseMode.HTML`` to the *parse_mode*
parameter. The following tags are currently supported:

.. code-block:: text

    <b>bold</b>, <strong>bold</strong>

    <i>italic</i>, <em>italic</em>

    <u>underline</u>, <ins>underline</ins>

    <s>strike</s>, <strike>strike</strike>, <del>strike</del>

    <spoiler>spoiler</spoiler>

    <a href="https://pyrogram.org/">text URL</a>

    <a href="tg://user?id=123456789">inline mention</a>

    <code>inline fixed-width code</code>

    <emoji id="12345678901234567890">🔥</emoji>

    <pre>pre-formatted fixed-width code block</pre>

    <pre language="python">pre-formatted code block with language</pre>

.. note::

    All ``<``, ``>`` and ``&`` symbols that are not a part of a tag or an HTML
    entity must be replaced with the corresponding HTML entities (``&lt;``,
    ``&gt;`` and ``&amp;``). You can use ``html.escape(text)`` to quickly escape
    those characters.

Different Styles
----------------

By default, when ignoring the *parse_mode* parameter, both Markdown and HTML
styles are enabled together. This means you can combine both syntaxes in the
same text:

.. code-block:: python

    await app.send_message("me", "**bold**, <i>italic</i>")

If you don't like this behaviour you can always choose to only enable either
Markdown or HTML in strict mode by passing ``MARKDOWN`` or ``HTML`` as the
*parse_mode* argument. In case you want to completely turn off the style parser,
simply pass ``DISABLED``: the text will be sent as-is.

Nested and Overlapping Entities
-------------------------------

You can also style texts with more than one decoration at once by nesting
entities together. Here are some example texts you can try sending:

**Markdown:**

- ``**bold, --underline--**``
- ``**bold __italic --underline ~~strike~~--__**``
- ``**bold __and** italic__``

**HTML:**

- ``<b>bold, <u>underline</u></b>``
- ``<b>bold <i>italic <u>underline <s>strike</s></u></i></b>``
- ``<b>bold <i>and</b> italic</i>``

**Combined:**

- ``--you can combine <i>HTML</i> with **Markdown**--``
- ``**and also <i>overlap** --entities</i> this way--``

.. note::

    Rich messages use a different, server-side formatting mechanism. See
    :doc:`rich-text` for details.
